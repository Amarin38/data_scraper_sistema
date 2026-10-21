// items = [{ titulo, valor, detalle?, tono? }]
export default function Kpis({ items }) {
  return (
    <div className="kpis">
      {items.map((k) => (
        <div key={k.titulo} className={`kpi${k.tono ? ` ${k.tono}` : ""}`}>
          <span className="kpi-titulo">{k.titulo}</span>
          <span className="kpi-valor">{k.valor}</span>
          {k.detalle && <span className="kpi-detalle">{k.detalle}</span>}
        </div>
      ))}
    </div>
  );
}
