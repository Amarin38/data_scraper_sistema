function paginasVisibles(actual, total) {
  const set = new Set([
    0,
    total - 1,
    actual - 2,
    actual - 1,
    actual,
    actual + 1,
    actual + 2,
  ]);
  const nums = [...set]
    .filter((n) => n >= 0 && n < total)
    .sort((a, b) => a - b);
  const res = [];
  nums.forEach((n, i) => {
    if (i > 0 && n - nums[i - 1] > 1) res.push("…");
    res.push(n);
  });
  return res;
}

export default function Paginacion({
  modo,
  pagina,
  totalPaginas,
  total,
  hayMas,
  onAnterior,
  onSiguiente,
  onIr,
}) {
  const haySiguiente = modo === "offset" ? pagina < totalPaginas - 1 : hayMas;
  return (
    <nav className="paginacion" aria-label="Paginación">
      <div className="pag-grupo">
        <button
          className="pag-nav"
          disabled={pagina === 0}
          onClick={onAnterior}
          aria-label="Anterior"
        >
          ‹
        </button>

        {modo === "offset" ? (
          paginasVisibles(pagina, totalPaginas).map((n, i) =>
            n === "…" ? (
              <span key={`e${i}`} className="pag-puntos">
                …
              </span>
            ) : (
              <button
                key={n}
                className={n === pagina ? "pag activa" : "pag"}
                onClick={() => onIr(n)}
              >
                {n + 1}
              </button>
            ),
          )
        ) : (
          <span className="pag-puntos">Página {pagina + 1}</span>
        )}

        <button
          className="pag-nav"
          disabled={!haySiguiente}
          onClick={onSiguiente}
          aria-label="Siguiente"
        >
          ›
        </button>
      </div>

      {modo === "offset" && (
        <span className="pag-info">
          {(total ?? 0).toLocaleString("es-AR")} resultados
        </span>
      )}
    </nav>
  );
}
