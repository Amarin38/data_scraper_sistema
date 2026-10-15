import Tabla from "../../components/grafico/Tabla.jsx";
import SelectConjuntos from "../../components/SelectConjuntos.jsx";
import PanelDetalle from "./PanelDetalle.jsx";
import Paginacion from "../../components/grafico/Paginacion.jsx";
import { useEffect, useState, useMemo, useRef } from "react";
import { getIndicesConsumo, getConjuntos } from "./api";

const columnas_indices = [
  {
    titulo: "Codigo",
    campo: "Codigo",
    claveOrden: "Codigo",
    alinear: "centro",
  },
  {
    titulo: "Repuesto",
    campo: "Descripcion",
    claveOrden: "Descripcion",
    alinear: "izquierda",
  },
  {
    titulo: "Peor cabecera",
    campo: "PeorCabecera",
    claveOrden: "MaxRelativo",
    alinear: "centro",
    render: (f) => {
      const v = Number(f.MaxRelativo);
      const color = v > 1.3 ? "#d64545" : v < 0.8 ? "#2e9e5b" : "#999";
      return (
        <span style={{ color, fontWeight: 600 }}>
          {f.PeorCabecera} {v.toFixed(1)}
        </span>
      );
    },
  },
  {
    titulo: "Rojas",
    campo: "CantRojas",
    claveOrden: "CantRojas",
    alinear: "centro",
    render: (f) => <span title={f.NombresRojas}>{f.CantRojas}</span>,
  },
];

export default function IndicesConsumoPage() {
  const [filas, setFilas] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);

  const [conjunto, setConjunto] = useState("");
  const [conjuntos, setConjuntos] = useState([]);
  const [texto, setTexto] = useState("");
  const [orden, setOrden] = useState({ campo: "MaxRelativo", dir: "desc" });

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const [cursores, setCursores] = useState([null]);
  const [pagina, setPagina] = useState(0);
  const [nextCursor, setNextCursor] = useState(null);

  // resize
  const [anchoPanel, setAnchoPanel] = useState(800); // en px
  const [arrastrando, setArrastrando] = useState(false);
  const contenidoRef = useRef(null); // para medir el libro

  useEffect(() => {
    getConjuntos().then(setConjuntos).catch(console.error);
  }, []);

  useEffect(() => {
    const c = cursores[pagina];
    const t = setTimeout(() => {
      setCargando(true);
      setError(null);
      getIndicesConsumo({
        conjunto,
        texto,
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
  }, [conjunto, texto, pagina, cursores]);

  const filasOrdenadas = useMemo(() => {
    const k = orden.campo;
    const signo = orden.dir === "asc" ? 1 : -1;
    return [...filas].sort((a, b) => {
      if (k === "Descripcion" || k === "Codigo") {
        return (
          signo *
          String(a[k]).localeCompare(String(b[k]), "es", { numeric: true })
        );
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

  function cambiarConjunto(c) {
    setConjunto(c);
    resetPaginacion();
  }

  function cambiarTexto(t) {
    setTexto(t);
    resetPaginacion();
  }

  function cambiarOrden(campo) {
    setOrden((o) =>
      o.campo === campo
        ? { campo, dir: o.dir === "desc" ? "asc" : "desc" }
        : { campo, dir: campo === "Descripcion" ? "asc" : "desc" },
    );
  }

  function empezarArrastre(e) {
    e.preventDefault();
    setArrastrando(true);
    const caja = contenidoRef.current.getBoundingClientRect();

    function mover(ev) {
      const nuevo = caja.right - ev.clientX;
      // mínimo 300px para el panel y 300px para la tabla
      setAnchoPanel(Math.min(Math.max(nuevo, 300), caja.width - 300));
    }
    function soltar() {
      setArrastrando(false);
      window.removeEventListener("pointermove", mover);
      window.removeEventListener("pointerup", soltar);
    }
    window.addEventListener("pointermove", mover);
    window.addEventListener("pointerup", soltar);
  }

  return (
    <>
      <div className="pagina">
        <div className="filtros">
          <SelectConjuntos
            conjuntos={conjuntos}
            conjunto={conjunto}
            setConjunto={cambiarConjunto}
          />
          <input
            value={texto}
            onChange={(e) => cambiarTexto(e.target.value)}
            placeholder="Buscar..."
          />
        </div>

        <div
          ref={contenidoRef}
          className={`contenido${seleccionado ? " con-panel" : ""}${arrastrando ? " arrastrando" : ""}`}
          style={{ "--ancho-panel": `${anchoPanel}px` }}
        >
          <div className="columna-tabla">
            {error && <p className="error">Error: {error}</p>}

            <div
              className="tabla-scroll"
              style={{ opacity: cargando ? 0.5 : 1 }}
            >
              {cargando && (
                <div className="spinner" role="status" aria-label="Cargando" />
              )}
              <Tabla
                nombreTabla={"tabla-indices"}
                nombreScroll={"scroll-indices"}
                columnas={columnas_indices}
                filas={filasOrdenadas}
                orden={orden}
                onOrdenar={cambiarOrden}
                pkFila={"IDRepuesto"}
                seleccionada={seleccionado?.IDRepuesto}
                onSeleccionar={setSeleccionado}
              />
            </div>
            <Paginacion
              pagina={pagina}
              hayMas={!!nextCursor}
              onAnterior={anterior}
              onSiguiente={siguiente}
            />
          </div>
          <aside className="panel">
            <div className="panel-interior">
              {seleccionado && (
                <div className="divisor" onPointerDown={empezarArrastre} />
              )}
              {seleccionado && (
                <>
                  <button onClick={() => setSeleccionado(null)}>
                    ✕ Cerrar
                  </button>
                  <PanelDetalle repuesto={seleccionado} />
                </>
              )}
            </div>
          </aside>
        </div>
      </div>
    </>
  );
}
