import { useState, useMemo, useEffect, useCallback } from "react";
import EstadoCarga from "../loading/EstadoCarga.jsx";
import Paginacion from "./Paginacion.jsx";
import BotonDescargar from "./BotonDescargar.jsx";
import Spinner from "../loading/Spinner.jsx";

// ancho en px de una columna fija (si no declara `ancho`, 100)
const anchoFijo = (c) => parseFloat(c.ancho) || 100;

export default function Tabla({
  datosTabla,
  columnas,
  filtros,
  ordenCol,
  ordenDir,
  pkFila,
  claseFila,
  paginacion,
  seleccionado,
  panelAbierto,
  onSeleccionar,
  exportar,
  ordenServidor = false,
}) {
  const [orden, setOrden] = useState({
    campo: ordenCol,
    dir:
      ordenDir ??
      (ordenServidor || ordenCol === "Descripcion" ? "asc" : "desc"),
  });
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
    if (ordenServidor) {
      setPagina(0);
      setCursores([null]);
    }
  }, [orden, ordenServidor]);

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
      const ordenParams = ordenServidor
        ? { orden: orden.campo, direccion: orden.dir }
        : {};
      datosTabla({ ...filtros, limit: LIMITE, ...params, ...ordenParams })
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
  }, [filtros, pagina, cursores, datosTabla, paginacion, ordenServidor, orden]);

  const filasOrdenadas = useMemo(() => {
    if (ordenServidor) return filas;
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
  }, [filas, orden, ordenServidor]);

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

  const columnasVisibles = useMemo(
    () =>
      panelAbierto ? columnas.filter((c) => !c.ocultarConPanel) : columnas,
    [columnas, panelAbierto],
  );

  // columnas fijas a la izquierda: el `left` de cada una es la suma de los anchos de las anteriores
  const { leftFija, ultimaFija } = useMemo(() => {
    const leftFija = {};
    let acum = 0;
    let ultimaFija = null;
    for (const c of columnasVisibles) {
      if (!c.fija) continue;
      leftFija[c.campo] = acum;
      acum += anchoFijo(c);
      ultimaFija = c.campo;
    }
    return { leftFija, ultimaFija };
  }, [columnasVisibles]);

  const clasesCol = (c) =>
    [
      claseAlin(c),
      c.fija && "col-fija",
      c.campo === ultimaFija && "col-fija-ult",
    ]
      .filter(Boolean)
      .join(" ");

  const estiloFija = (c) =>
    c.fija
      ? {
          left: leftFija[c.campo],
          width: anchoFijo(c),
          minWidth: anchoFijo(c),
          maxWidth: anchoFijo(c),
        }
      : undefined;

  const botonExportar = exportar && (
    <BotonDescargar
      ruta={exportar.ruta}
      nombre={exportar.nombre}
      filtros={filtros}
      orden={ordenServidor ? orden : null}
    />
  );

  return (
    <div className="columna-tabla">
      <div className="tabla-marco">
        <EstadoCarga
          className="tabla-scroll"
          cargando={cargando}
          error={error}
          spinner={false}
        >
          <div className="scroll-repuestos">
            <table className="tabla-repuestos">
              <thead>
                <tr>
                  {columnasVisibles.map((col) => (
                    <th
                      key={col.campo}
                      className={clasesCol(col)}
                      style={{
                        width: col.ancho,
                        cursor: col.claveOrden ? "pointer" : "default",
                        ...estiloFija(col),
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
                      {columnasVisibles.map((col) => (
                        <td
                          key={col.campo}
                          className={clasesCol(col)}
                          style={estiloFija(col)}
                        >
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
        {cargando && (
          <div className="tabla-bloqueo">
            <Spinner />
          </div>
        )}
      </div>
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
