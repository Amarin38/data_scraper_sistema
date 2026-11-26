import { useCallback, useEffect, useRef, useState } from "react";
import PanelLateral from "../components/grafico/PanelLateral.jsx";
import Celda from "../components/grafico/Celda.jsx";
import Miniatura from "../components/grafico/Miniatura.jsx";
import { datos_rapidos_ep } from "../constants.js";
import { getCacheado } from "../api/client.js";
import { useMasonry } from "../hooks/useMasonry.js";
import { useTablero } from "../hooks/useTablero.js";
import { vistas } from "./repuestos/vistasRepuesto.js";
import {
  PANELES,
  PANELES_POR_ID,
  POR_DEFECTO,
} from "../modulos/PanelesInicio.jsx";

const getDatosRapidos = () => getCacheado(datos_rapidos_ep);

export default function InicioPage() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const [seleccionado, setSeleccionado] = useState(null);
  const [editando, setEditando] = useState(false);
  const idSel = seleccionado?.IDRepuesto;

  const {
    listo,
    ids,
    anchos,
    bloques,
    permitidos,
    fijarAncho,
    mover,
    agregar,
    quitar,
    restablecer,
    personalizado,
    guardar,
    descartar,
  } = useTablero(POR_DEFECTO);

  const [guardando, setGuardando] = useState(false);
  const [errorGuardado, setErrorGuardado] = useState(false);

  const terminar = async () => {
    setGuardando(true);
    const ok = await guardar();
    setGuardando(false);
    setErrorGuardado(!ok);
    if (ok) setEditando(false);
  };

  const cancelar = useCallback(() => {
    descartar();
    setErrorGuardado(false);
    setEditando(false);
  }, [descartar]);

  const refTarjetas = useRef(null);
  useMasonry(refTarjetas, JSON.stringify([ids, anchos, bloques]));

  // la animación de entrada se reinicia cada vez que el navegador mueve un nodo: solo se usa al cargar
  const [entrando, setEntrando] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => setEntrando(false), 800);
    return () => clearTimeout(t);
  }, []);

  // /datos_rapidos se pide solo si hay algún panel visible que lo use (y una sola vez)
  const necesitaRapidos = ids.some(
    (id) => PANELES_POR_ID[id]?.fuente === "rapidos",
  );
  useEffect(() => {
    if (!necesitaRapidos || datos) return;
    let cancelado = false;
    setError(null);
    getDatosRapidos()
      .then((d) => !cancelado && setDatos(d))
      .catch(
        (e) =>
          !cancelado &&
          setError(e.message ?? "No se pudieron cargar los datos"),
      );
    return () => {
      cancelado = true;
    };
  }, [necesitaRapidos, datos]);

  // Escape cancela la edición (descarta los cambios)
  useEffect(() => {
    if (!editando) return;
    const tecla = (e) => e.key === "Escape" && cancelar();
    document.addEventListener("keydown", tecla);
    return () => document.removeEventListener("keydown", tecla);
  }, [editando, cancelar]);

  const ctx = {
    datos,
    cargando: necesitaRapidos && !datos && !error,
    error,
    onSeleccionar: setSeleccionado,
    seleccionado: idSel,
  };
  // bandeja "Agregar panel": no visibles y autorizados para este usuario (null = todavía no se sabe)
  const ocultos = PANELES.filter(
    (p) =>
      !ids.includes(p.id) && (permitidos == null || permitidos.includes(p.id)),
  );

  return (
    <div className={`inicio${editando ? " editando" : ""}`}>
      <header className="inicio-cabecera">
        <div>
          <div className="inicio-titulo">
            <h1>Estadísticas rápidas</h1>
            {editando ? (
              <>
                <button
                  type="button"
                  className="inicio-editar activo"
                  onClick={terminar}
                  disabled={guardando}
                >
                  {guardando ? "Guardando…" : "Listo"}
                </button>
                <button
                  type="button"
                  className="inicio-reset"
                  onClick={cancelar}
                  disabled={guardando}
                >
                  Cancelar
                </button>
              </>
            ) : (
              <button
                type="button"
                className="inicio-editar"
                onClick={() => setEditando(true)}
              >
                Editar
              </button>
            )}
            {errorGuardado && (
              <span
                role="alert"
                style={{ color: "#dc2626", fontSize: "0.85rem" }}
              >
                No se pudo guardar. Reintentá.
              </span>
            )}{" "}
          </div>
          <p>Resumen de estadísticas rápidas del sistema.</p>
        </div>
      </header>

      {editando && (
        <section className="inicio-edicion" aria-label="Agregar paneles">
          <div className="inicio-edicion-cab">
            <span className="inicio-edicion-titulo">Agregar panel</span>
            {personalizado && (
              <button
                type="button"
                className="inicio-reset"
                onClick={restablecer}
              >
                Restablecer disposición
              </button>
            )}
          </div>
          {ocultos.length > 0 ? (
            <div className="inicio-edicion-lista">
              {ocultos.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className="inicio-agregar"
                  onClick={() => agregar(p.id)}
                >
                  <Miniatura vista={p.vista} />
                  <span className="inicio-agregar-pie">
                    <span className="inicio-agregar-titulo">{p.titulo}</span>
                    <span className="inicio-agregar-mas" aria-hidden="true">
                      +
                    </span>
                  </span>
                  <span className="inicio-agregar-desc">{p.descripcion}</span>
                </button>
              ))}
            </div>
          ) : (
            <p className="inicio-edicion-vacio">
              Ya están todos los paneles en pantalla.
            </p>
          )}
        </section>
      )}

      {listo && ids.length === 0 && (
        <p className="inicio-vacio">
          No hay paneles. Tocá <b>Editar</b> para agregar.
        </p>
      )}

      <div
        className={`tarjetas${entrando ? "" : " sin-entrada"}`}
        ref={refTarjetas}
      >
        {ids.map((id) => {
          const { Componente, titulo } = PANELES_POR_ID[id];
          return (
            <Celda
              key={id}
              id={id}
              titulo={titulo}
              ancho={anchos[id]}
              bloque={bloques[id]}
              editando={editando}
              onAncho={fijarAncho}
              onMover={mover}
              onQuitar={quitar}
            >
              <Componente {...ctx} />
            </Celda>
          );
        })}
      </div>

      <div className={`inicio-drawer${seleccionado ? " con-panel" : ""}`}>
        <PanelLateral
          vistas={vistas}
          subtitulo=""
          seleccionado={seleccionado}
          setSeleccionado={setSeleccionado}
        />
      </div>
    </div>
  );
}
