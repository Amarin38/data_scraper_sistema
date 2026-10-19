import { useEffect, useState, useMemo, useRef, useCallback } from "react";
import Filtros from "./Filtros.jsx";
import Tabla from "./Tabla.jsx";
import Paginacion from "./Paginacion.jsx";
import PanelLateral from "./PanelLateral.jsx";
import EstadoCarga from "../loading/EstadoCarga.jsx";

export default function TablaGrafico({
  datosTabla,
  vistas,
  subtitulo,
  columnas,
  ordenCol,
  pkFila,
}) {
  const [filas, setFilas] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);

  const [cursores, setCursores] = useState([null]);
  const [pagina, setPagina] = useState(0);
  const [nextCursor, setNextCursor] = useState(null);

  const [anchoPanel, setAnchoPanel] = useState(800); // en px
  const [arrastrando, setArrastrando] = useState(false);
  const contenidoRef = useRef(null); // para medir el libro

  const [filtros, setFiltros] = useState({
    conjunto: "",
    descripcion: "",
    codigo: "",
  });
  const [orden, setOrden] = useState({ campo: ordenCol, dir: "desc" });

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const c = cursores[pagina];
    const t = setTimeout(() => {
      setCargando(true);
      setError(null);
      datosTabla({
        ...filtros,
        limit: 50,
        cursor_valor: c?.valor,
        cursor_id: c?.id,
      })
        .then((d) => {
          setFilas(d.items);
          setNextCursor(d.next_cursor);
        })
        .catch((err) => setError(err.message))
        .finally(() => setCargando(false));
    }, 300);
    return () => clearTimeout(t);
  }, [filtros, pagina, cursores, datosTabla]);

  const cambiarFiltros = useCallback((f) => {
    setFiltros(f);
    setCursores([null]);
    setPagina(0);
  }, []);

  const filasOrdenadas = useMemo(() => {
    const k = orden.campo;
    const signo = orden.dir === "asc" ? 1 : -1;
    return [...filas].sort((a, b) => {
      if (
        k === "Descripcion" ||
        k === "Codigo" ||
        k === "Condicion" ||
        k === "Conjunto"
      ) {
        return (
          signo *
          String(a[k]).localeCompare(String(b[k]), "es", { numeric: true })
        );
      }
      if (k === "Critico") {
        return signo * (Number(!!a[k]) - Number(!!b[k]));
      }
      return signo * (Number(a[k]) - Number(b[k]));
    });
  }, [filas, orden]);

  function siguiente() {
    setCursores((prev) => {
      const copia = prev.slice(0, pagina + 1);
      copia[pagina + 1] = nextCursor;
      return copia;
    });
    setPagina(pagina + 1);
  }

  function anterior() {
    setPagina(pagina - 1);
  }

  function resetPaginacion() {
    setCursores([null]);
    setPagina(0);
  }

  function cambiarOrden(campo) {
    setOrden((o) =>
      o.campo === campo
        ? { campo, dir: o.dir === "desc" ? "asc" : "desc" }
        : { campo, dir: campo === "Descripcion" ? "asc" : "desc" },
    );
  }

  return (
    <div className="pagina">
      <Filtros onCambio={cambiarFiltros} reset={resetPaginacion} />

      <div
        ref={contenidoRef}
        className={`contenido${seleccionado ? " con-panel" : ""}${arrastrando ? " arrastrando" : ""}`}
        style={{ "--ancho-panel": `${anchoPanel}px` }}
      >
        <div className="columna-tabla">
          <EstadoCarga
            className="tabla-scroll"
            cargando={cargando}
            error={error}
          >
            <Tabla
              nombreTabla={"tabla-repuestos"}
              nombreScroll={"scroll-repuestos"}
              columnas={columnas}
              filas={filasOrdenadas}
              orden={orden}
              onOrdenar={cambiarOrden}
              pkFila={pkFila}
              seleccionada={seleccionado?.IDRepuesto}
              onSeleccionar={setSeleccionado}
            />
          </EstadoCarga>
          <Paginacion
            pagina={pagina}
            hayMas={!!nextCursor}
            onAnterior={anterior}
            onSiguiente={siguiente}
          />
        </div>
        <PanelLateral
          vistas={vistas}
          subtitulo={subtitulo}
          seleccionado={seleccionado}
          setSeleccionado={setSeleccionado}
        />
      </div>
    </div>
  );
}
