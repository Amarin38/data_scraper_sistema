import { useEffect, useState } from "react";

// escritorio: primera, última y 2 a cada lado de la actual (páginas desde 0)
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

// celular: siempre las mismas 5 posiciones, así el grupo no cambia de ancho
//   páginas 1-3      ->  1 2 3 … 516
//   páginas 4-513    ->  1 … N … 516
//   páginas 514-516  ->  1 … 514 515 516
function paginasMovil(actual, total, max = 5) {
  if (total <= max) return Array.from({ length: total }, (_, i) => i);
  const cola = max - 2; // botones del lado que no lleva "…"
  if (actual < cola)
    return [...Array.from({ length: cola }, (_, i) => i), "…", total - 1];
  if (actual > total - 1 - cola)
    return [
      0,
      "…",
      ...Array.from({ length: cola }, (_, i) => total - cola + i),
    ];
  return [0, "…", actual, "…", total - 1];
}

// ¿pantalla de celular? Se actualiza si girás o redimensionás
function useMovil(consulta = "(max-width: 768px)") {
  const [movil, setMovil] = useState(() => window.matchMedia(consulta).matches);
  useEffect(() => {
    const q = window.matchMedia(consulta);
    const cambio = () => setMovil(q.matches);
    q.addEventListener("change", cambio);
    return () => q.removeEventListener("change", cambio);
  }, [consulta]);
  return movil;
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
  izquierda,
}) {
  const movil = useMovil();
  const haySiguiente = modo === "offset" ? pagina < totalPaginas - 1 : hayMas;
  const items = movil
    ? paginasMovil(pagina, totalPaginas)
    : paginasVisibles(pagina, totalPaginas);

  return (
    <nav className="paginacion" aria-label="Paginación">
      {izquierda && <div className="pag-izquierda">{izquierda}</div>}
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
          items.map((n, i) =>
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
          <span className="pag-puntos pag-texto">Página {pagina + 1}</span>
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
