// columnas: [{ campo, titulo, formatoLista?, destacada? }]
// con más de una columna se muestra un encabezado con los títulos
export default function ListaRanking({
  filas,
  codigo,
  descripcion,
  columnas,
  titulo = "Repuesto",
  barra, // campo que define el largo de la barra (por defecto, la última columna)
  color = "#3b82f6",
  posicion = true,
}) {
  if (!Array.isArray(filas) || !filas.length) return null;

  const campoBarra = barra ?? columnas[columnas.length - 1].campo;
  const max = Math.max(...filas.map((f) => Number(f[campoBarra])), 1);
  const multi = columnas.length > 1;
  const plantilla = `${posicion ? "22px " : ""}1fr ${columnas
    .map(() => (multi ? "var(--w-col, 72px)" : "auto"))
    .join(" ")}`;

  const fmt = (c) =>
    c.formatoLista ?? c.formatoTitulo ?? c.formato ?? ((v) => v);
  const claseValor = (c) =>
    c.destacada ? "lb-importar" : multi ? undefined : "rk-valor";

  return (
    <div className="lista-barras">
      {multi && (
        <div
          className="lb-fila lb-cab"
          style={{ gridTemplateColumns: plantilla }}
        >
          {posicion && <span />}
          <span className="lb-nombre">{titulo}</span>
          {columnas.map((c) => (
            <span key={c.campo}>{c.titulo}</span>
          ))}
        </div>
      )}
      {filas.map((f, i) => (
        <div
          className="lb-fila"
          key={f.IDRepuesto ?? f[codigo]}
          style={{ gridTemplateColumns: plantilla }}
          title={descripcion ? f[descripcion] : undefined}
        >
          {posicion && <span className="rk-pos">{i + 1}</span>}
          <span className="lb-nombre">
            <b>{f[codigo]}</b> {descripcion ? f[descripcion] : ""}
          </span>
          {columnas.map((c) => (
            <span key={c.campo} className={claseValor(c)}>
              {fmt(c)(f[c.campo])}
            </span>
          ))}
          <i
            className="lb-barra"
            style={{
              width: `${(Number(f[campoBarra]) / max) * 100}%`,
              background: color,
            }}
          />
        </div>
      ))}
    </div>
  );
}
