import { useState, useMemo, useEffect, useCallback } from "react";
import EstadoCarga from "../loading/EstadoCarga.jsx";
import Paginacion from "./Paginacion.jsx";
import BotonDescargar from "./BotonDescargar.jsx";

export default function Tabla({
  datosTabla,
  columnas,
  filtros,
  ordenCol,
  pkFila,
  claseFila,
  paginacion,
  seleccionado,
  onSeleccionar,
  exportar,
}) {
  const [orden, setOrden] = useState({ campo: ordenCol, dir: "desc" });
  const [filas, setFilas] = useState([]);

  const [pagina, setPagina] = useState(0);

  const [cursores, setCursores] = useState([null]);
  const [nextCursor, setNextCursor] = useState(null);

  const [total, setTotal] = useState(0);
  const LIMITE = 50;
  const totalPaginas = Math.max(1, Math.ceil(total / LIMITE));

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setPagina(0);
    setCursores([null]);
  }, [filtros]);

  useEffect(() => {
    if (!filtros) return;
    let cancelado = false;
    const t = setTimeout(() => {
      const c = cursores[pagina];
      const params =
        paginacion === "cursor"
          ? { cursor_valor: c?.valor, cursor_id: c?.id }
          : { page: pagina };

      setCargando(true);
      setError(null);
      datosTabla({ ...filtros, limit: LIMITE, ...params })
        .then((d) => {
          if (cancelado) return;
          setFilas(d.items);
          setNextCursor(d.next_cursor ?? null);
          setTotal(d.total ?? 0);
        })
        .catch((e) => {
          if (!cancelado) setError(e.message);
        })
        .finally(() => {
          if (!cancelado) setCargando(false);
        });
    }, 300);
    return () => {
      cancelado = true;
      clearTimeout(t);
    };
  }, [filtros, pagina, cursores, datosTabla, paginacion]);

  const filasOrdenadas = useMemo(() => {
    const k = orden.campo;
    const signo = orden.dir === "asc" ? 1 : -1;
    const col = columnas.find((c) => c.claveOrden === k);
    const esTexto = col?.tipo === "texto";
    const esBool = col?.tipo === "bool";
    const esNum = col?.tipo === "numeric";

    return [...filas].sort((a, b) => {
      if (esTexto)
        return (
          signo *
          String(a[k] ?? "").localeCompare(String(b[k] ?? ""), "es", {
            numeric: true,
          })
        );
      if (esBool) return signo * (Number(!!a[k]) - Number(!!b[k]));
      if (esNum) return signo * (Number(a[k]) - Number(b[k]));
    });
  }, [filas, orden]);

  function cambiarOrden(campo) {
    setOrden((o) =>
      o.campo === campo
        ? { campo, dir: o.dir === "desc" ? "asc" : "desc" }
        : { campo, dir: campo === "Descripcion" ? "asc" : "desc" },
    );
  }

  function siguiente() {
    if (paginacion === "cursor") {
      setCursores((prev) => {
        const copia = prev.slice(0, pagina + 1);
        copia[pagina + 1] = nextCursor; // guardar ANTES de avanzar
        return copia;
      });
    }
    setPagina(pagina + 1);
  }

  function anterior() {
    setPagina(pagina - 1);
  }

  const claseAlin = (c) => (c.alinear ? `alin-${c.alinear}` : "");

  const botonExportar = exportar && (
    <BotonDescargar
      ruta={exportar.ruta}
      nombre={exportar.nombre}
      filtros={filtros}
    />
  );

  return (
    <div className="columna-tabla">
      <EstadoCarga className="tabla-scroll" cargando={cargando} error={error}>
        <div className="scroll-repuestos">
          <table className="tabla-repuestos">
            <thead>
              <tr>
                {columnas.map((col) => (
                  <th
                    key={col.campo}
                    className={claseAlin(col)}
                    style={{
                      width: col.ancho,
                      cursor: col.claveOrden ? "pointer" : "default",
                    }}
                    onClick={
                      col.claveOrden
                        ? () => cambiarOrden(col.claveOrden)
                        : undefined
                    }
                  >
                    {col.titulo}
                    {orden?.campo === col.claveOrden && (
                      <span className={`flecha ${orden.dir}`} />
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filasOrdenadas.map((fil) => {
                const id = fil[pkFila];
                return (
                  <tr
                    key={id}
                    className={`${id === seleccionado ? "sel" : ""} ${claseFila?.(fil) ?? ""}`.trim()}
                    onClick={() => onSeleccionar?.(fil)}
                  >
                    {columnas.map((col) => (
                      <td key={col.campo} className={claseAlin(col)}>
                        {col.render ? col.render(fil) : fil[col.campo]}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </EstadoCarga>
      <Paginacion
        modo={paginacion}
        pagina={pagina}
        totalPaginas={totalPaginas}
        total={total}
        hayMas={!!nextCursor}
        onAnterior={anterior}
        onSiguiente={siguiente}
        onIr={setPagina}
        izquierda={botonExportar}
      />
    </div>
  );
}
