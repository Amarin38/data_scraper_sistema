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
  children,
  alto,
  acento,
  acciones, // nodo opcional entre el detalle y el gráfico (fuera de .tarjeta-grafico)
  accionesTitulo, // nodo opcional arriba a la derecha de la tarjeta
}) {
  return (
    <section
      className={`tarjeta ${tono ?? ""}`}
      style={{
        gridColumn: `span ${cols}`,
        ...(acento ? { "--acento-tarjeta": acento } : {}),
      }}
    >
      <span className="tarjeta-titulo">{titulo}</span>
      {accionesTitulo && (
        <div className="tarjeta-acciones-arriba">{accionesTitulo}</div>
      )}
      <EstadoCarga
        cargando={cargando}
        error={error}
        vacio={vacio}
        mensajeVacio="Sin datos"
      >
        <div className="tarjeta-valor">{valor}</div>
        {detalle && <div className="tarjeta-detalle">{detalle}</div>}
        {acciones && <div className="tarjeta-acciones">{acciones}</div>}
        <div
          className="tarjeta-grafico"
          style={alto ? { height: alto } : undefined}
        >
          {children}
        </div>
      </EstadoCarga>
    </section>
  );
}
