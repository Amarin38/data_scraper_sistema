/**
 * Vista previa esquemática de un panel (sin datos reales ni pedidos al backend).
 * `vista`: { titulo, valor, color, pildoras?, filas?: number[] (largo de cada barra, %), sinBarra? }
 */
export default function Miniatura({ vista }) {
  const {
    titulo,
    valor,
    color,
    pildoras = 0,
    filas = [],
    sinBarra = false,
  } = vista;
  return (
    <div
      className={`mini${sinBarra ? " sin-barra" : ""}`}
      style={{ "--tono": color }}
      aria-hidden="true"
    >
      <div className="mini-titulo">{titulo}</div>
      <div className="mini-valor">{valor}</div>
      {pildoras > 0 && (
        <div className="mini-pildoras">
          {Array.from({ length: pildoras }, (_, i) => (
            <span key={i} className={i === 0 ? "act" : ""} />
          ))}
        </div>
      )}
      <div className="mini-filas">
        {filas.map((w, i) => (
          <div key={i} className="mini-fila">
            <span className="mini-cod" />
            <span
              className="mini-txt"
              style={{ width: `${88 - ((i * 17) % 40)}%` }}
            />
            <span className="mini-num" />
            {!sinBarra && (
              <span className="mini-barra" style={{ width: `${w}%` }} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
