import { fmt_spark } from "../../constants.js";

export default function ListaImportar({ filas, color = "#6366f1" }) {
  if (!filas.length) return null;

  const max = Math.max(...filas.map((f) => Number(f.Faltante)), 1);

  return (
    <div className="lista-barras">
      <div className="lb-fila lb-cab">
        <span className="lb-nombre">Repuesto</span>
        <span>Previsto</span>
        <span>Stock</span>
        <span>Importar</span>
      </div>
      {filas.map((f) => (
        <div className="lb-fila" key={f.IDRepuesto} title={f.Descripcion}>
          <span className="lb-nombre">
            <b>{f.Codigo}</b> {f.Descripcion}
          </span>
          <span>{fmt_spark.format(Number(f.Prevision))}</span>
          <span>{fmt_spark.format(Number(f.Stock))}</span>
          <span className="lb-importar">
            {fmt_spark.format(Math.ceil(Number(f.Faltante)))}
          </span>
          <i
            className="lb-barra"
            style={{
              width: `${(Number(f.Faltante) / max) * 100}%`,
              background: color,
            }}
          />
        </div>
      ))}
    </div>
  );
}
