import Spinner from "./Spinner.jsx";

export default function EstadoCarga({
  cargando,
  error,
  vacio = false,
  mensajeVacio = "Sin datos.",
  className = "",
  children,
}) {
  return (
    <div className={`estado-carga ${className}`}>
      {error && <p className="error">Error: {error}</p>}
      {!error && !cargando && vacio && <p className="vacio">{mensajeVacio}</p>}

      {/* siempre montado: se atenúa mientras carga */}
      <div
        className={cargando ? "estado-contenido cargando" : "estado-contenido"}
      >
        {children}
      </div>

      {cargando && <Spinner />}
    </div>
  );
}
