// items = [{ titulo, valor, detalle?, tono? }]
const claseLargo = (v) =>
  typeof v === "string" && v.length > 9 ? " largo" : "";

export default function Kpis({ items, className = "" }) {
  return (
    <div className={`kpis ${className}`.trim()}>
      {items.map((k) => (
        <div key={k.titulo} className={`kpi${k.tono ? ` ${k.tono}` : ""}`}>
          <span className="kpi-titulo">{k.titulo}</span>
          <span className={`kpi-valor${claseLargo(k.valor)}`}>{k.valor}</span>
          {k.detalle && <span className="kpi-detalle">{k.detalle}</span>}
        </div>
      ))}
    </div>
  );
}
