import EstadoCarga from "../loading/EstadoCarga.jsx";

export default function TarjetaMicro({
  titulo,
  valor,
  detalle,
  tono,
  cargando,
  error,
  vacio,
  cols = 1,
  alto,
  children,
}) {
  return (
    <section
      className={`tarjeta ${tono ?? ""}`}
      style={{ gridColumn: `span ${cols}`, height: alto }}
    >
      <span className="tarjeta-titulo">{titulo}</span>
      <EstadoCarga
        cargando={cargando}
        error={error}
        vacio={vacio}
        mensajeVacio="Sin datos"
      >
        <div className="tarjeta-valor">{valor}</div>
        {detalle && <div className="tarjeta-detalle">{detalle}</div>}
        <div className="tarjeta-grafico">{children}</div>
      </EstadoCarga>
    </section>
  );
}
