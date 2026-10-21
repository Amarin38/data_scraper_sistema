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
  hayMas,
  onAnterior,
  onSiguiente,
  onIr,
}) {
  const haySiguiente = modo === "offset" ? pagina < totalPaginas - 1 : hayMas;

  return (
    <div className="paginacion">
      <button disabled={pagina === 0} onClick={onAnterior}>
        ‹ Anterior
      </button>

      {modo === "offset" ? (
        paginasVisibles(pagina, totalPaginas).map((n, i) =>
          n === "…" ? (
            <span key={`e${i}`}>…</span>
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
        <span>Página {pagina + 1}</span>
      )}

      <button disabled={!haySiguiente} onClick={onSiguiente}>
        Siguiente ›
      </button>
    </div>
  );
}
