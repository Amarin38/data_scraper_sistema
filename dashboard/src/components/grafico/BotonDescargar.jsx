import { useRef, useState } from "react";
import { abrirStream } from "../../api/client.js";

const FORMATOS = [
  {
    id: "xlsx",
    etiqueta: "Excel",
    ext: ".xlsx",
    mime: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  },
  { id: "csv", etiqueta: "CSV", ext: ".csv", mime: "text/csv" },
  { id: "json", etiqueta: "JSON", ext: ".json", mime: "application/json" },
];

const limpiar = (s) => s.replace(/[\\/:*?"<>|]/g, "").trim();
const puedeElegirUbicacion =
  typeof window !== "undefined" && "showSaveFilePicker" in window;
const mb = (n) => (n / 1048576).toFixed(0);

export default function BotonDescargar({ ruta, nombre, filtros, orden }) {
  const dialogo = useRef(null);
  const abortRef = useRef(null);
  const [nombreArchivo, setNombreArchivo] = useState("");
  const [formato, setFormato] = useState("xlsx");
  const [estado, setEstado] = useState({ cargando: false, error: "" });
  const [progreso, setProgreso] = useState(null);

  const fmt = FORMATOS.find((f) => f.id === formato);

  const abrir = () => {
    const fecha = new Date().toLocaleDateString("en-CA");
    setNombreArchivo(`${nombre}_${fecha}`);
    setEstado({ cargando: false, error: "" });
    setProgreso(null);
    dialogo.current.showModal();
  };
  const cerrar = () => dialogo.current.close();
  const cancelar = () => {
    abortRef.current?.abort();
    cerrar();
  };

  const guardar = async () => {
    const base = limpiar(nombreArchivo) || nombre;
    const archivo = `${base}${fmt.ext}`;
    const params = {
      ...filtros,
      formato,
      nombre: base,
      ...(orden ? { orden: orden.campo, direccion: orden.dir } : {}),
    };
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setEstado({ cargando: true, error: "" });
    setProgreso({ bytes: 0, filas: 0, total: null, totalBytes: null });
    let writable = null;
    try {
      // el selector tiene que abrirse primero, mientras el clic sigue "fresco"
      const handle = puedeElegirUbicacion
        ? await window.showSaveFilePicker({
            suggestedName: archivo,
            types: [
              { description: fmt.etiqueta, accept: { [fmt.mime]: [fmt.ext] } },
            ],
          })
        : null;

      // si el servidor rechaza (ej. Excel con más de 1.000.000 filas), falla acá, antes de bajar nada
      const res = await abrirStream(ruta, params, ctrl.signal);
      const total = Number(res.headers.get("X-Filas-Estimadas")) || null;
      const totalBytes = Number(res.headers.get("Content-Length")) || null;
      writable = handle ? await handle.createWritable() : null;

      const partes = [];
      const reader = res.body.getReader();
      let bytes = 0;
      let filas = 0;
      let ultimo = 0;
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        if (writable) await writable.write(value);
        else partes.push(value);
        bytes += value.length;
        if (formato === "csv")
          for (let i = 0; i < value.length; i++) if (value[i] === 10) filas++;
        const ahora = performance.now();
        if (ahora - ultimo > 200) {
          ultimo = ahora;
          setProgreso({ bytes, filas, total, totalBytes });
        }
      }

      if (writable) {
        await writable.close();
        writable = null;
      } else {
        const url = URL.createObjectURL(new Blob(partes, { type: fmt.mime }));
        const a = document.createElement("a");
        a.href = url;
        a.download = archivo;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      }
      setEstado({ cargando: false, error: "" });
      cerrar();
    } catch (e) {
      if (writable) await writable.abort().catch(() => {});
      const cancelo = e.name === "AbortError";
      setEstado({
        cargando: false,
        error: cancelo ? "" : e.message || "No se pudo exportar.",
      });
    } finally {
      abortRef.current = null;
      setProgreso(null);
    }
  };

  const pct = progreso?.totalBytes
    ? Math.min(100, Math.round((progreso.bytes * 100) / progreso.totalBytes))
    : progreso?.total && progreso.filas
      ? Math.min(99, Math.round((progreso.filas * 100) / progreso.total))
      : null;

  return (
    <>
      <button className="btn-descargar" onClick={abrir} disabled={!filtros}>
        <svg
          width="14"
          height="14"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M8 2v8M4.5 7 8 10.5 11.5 7M2.5 13.5h11" />
        </svg>
        Descargar
      </button>

      <dialog
        ref={dialogo}
        className="modal"
        onClick={(e) =>
          e.target === dialogo.current && !estado.cargando && cancelar()
        }
        onClose={() => abortRef.current?.abort()}
      >
        <div className="modal-caja">
          <h3>Descargar tabla</h3>
          <p className="modal-sub">
            Se exportan todas las filas que coinciden con los filtros actuales
            {orden ? ", en el orden que estás viendo" : ""}.
          </p>

          <label className="modal-campo">
            <span>Nombre del archivo</span>
            <div className="modal-nombre">
              <input
                value={nombreArchivo}
                disabled={estado.cargando}
                onChange={(e) => setNombreArchivo(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" && !estado.cargando && guardar()
                }
              />
              <em>{fmt.ext}</em>
            </div>
          </label>

          <div className="modal-campo">
            <span>Formato</span>
            <div className="modal-formatos">
              {FORMATOS.map((f) => (
                <button
                  key={f.id}
                  type="button"
                  disabled={estado.cargando}
                  className={f.id === formato ? "activo" : ""}
                  onClick={() => setFormato(f.id)}
                >
                  {f.etiqueta}
                  <small>{f.ext}</small>
                </button>
              ))}
            </div>
          </div>

          {progreso ? (
            <div className="modal-progreso">
              <progress max={100} value={pct ?? undefined} />
              <span>
                {progreso.bytes === 0
                  ? "Preparando el archivo en el servidor…"
                  : `${mb(progreso.bytes)} MB${formato === "csv" ? ` · ${progreso.filas.toLocaleString("es-AR")} filas` : ""}${pct !== null ? ` (~${pct} %)` : ""}`}
              </span>
            </div>
          ) : (
            <p className="modal-ubicacion">
              {puedeElegirUbicacion
                ? "Al guardar vas a poder elegir la carpeta."
                : "Este navegador guarda el archivo en Descargas. Con archivos muy grandes, usá Chrome o Edge."}
            </p>
          )}
          {estado.error && <p className="modal-error">{estado.error}</p>}

          <div className="modal-acciones">
            <button type="button" onClick={cancelar}>
              Cancelar
            </button>
            <button
              type="button"
              className="primario"
              onClick={guardar}
              disabled={estado.cargando}
            >
              {estado.cargando
                ? "Descargando…"
                : puedeElegirUbicacion
                  ? "Elegir carpeta y guardar"
                  : "Descargar"}
            </button>
          </div>
        </div>
      </dialog>
    </>
  );
}
