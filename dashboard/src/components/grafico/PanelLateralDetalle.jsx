import { useEffect, useState } from "react";
import Pestana from "./Pestana.jsx";
import EstadoCarga from "../loading/EstadoCarga.jsx";

export default function PanelLateralDetalle({
  vistas,
  repuesto,
  subtitulo,
  onCerrar,
}) {
  const pestanas = Object.keys(vistas);
  const [vista, setVista] = useState(pestanas[0]);
  const [resultado, setResultado] = useState({ vista: null, datos: null });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelado = false;
    setCargando(true);
    setError(null);
    vistas[vista]
      .get(repuesto.IDRepuesto)
      .then((d) => {
        if (!cancelado) setResultado({ vista, datos: d });
      })
      .catch((e) => {
        if (!cancelado) setError(e.message);
      })
      .finally(() => {
        if (!cancelado) setCargando(false);
      });
    return () => {
      cancelado = true;
    };
  }, [repuesto.IDRepuesto, vista, vistas]);

  const cargado = resultado.vista === vista;
  const datos = cargado ? resultado.datos : null;
  const hayDatos = Array.isArray(datos) ? datos.length > 0 : datos != null;
  const { Vista } = vistas[vista];

  return (
    <div className="panel-detalle">
      <Pestana
        items={pestanas}
        activa={vista}
        onCambiar={setVista}
        clase="panel-tab"
      >
        <button
          className="panel-tab cerrar"
          onClick={onCerrar}
          aria-label="Cerrar"
        >
          ✕
        </button>
      </Pestana>
      <div className="panel-cuerpo" style={{ opacity: cargando ? 0.5 : 1 }}>
        <h3>{repuesto.Descripcion}</h3>
        <p>{subtitulo}</p>
        <EstadoCarga
          cargando={cargando}
          error={error}
          vacio={cargado && !hayDatos}
          mensajeVacio="Sin datos para este repuesto."
        >
          {hayDatos && <Vista datos={datos} />}
        </EstadoCarga>
      </div>
    </div>
  );
}
