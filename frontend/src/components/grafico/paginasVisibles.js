import { useEffect, useState } from "react";

// Páginas a mostrar, siempre la misma cantidad de botones (max). null = "…"
// paginasVisibles(1, 516)   -> 1 2 3 … 516
// paginasVisibles(4, 516)   -> 1 … 4 … 516
// paginasVisibles(515, 516) -> 1 … 514 515 516
export function paginasVisibles(actual, total, max = 5) {
  if (total <= max) return Array.from({ length: total }, (_, i) => i + 1);
  const cola = max - 2; // botones del lado que no tiene "…"
  if (actual <= cola)
    return [...Array.from({ length: cola }, (_, i) => i + 1), null, total];
  if (actual > total - cola)
    return [
      1,
      null,
      ...Array.from({ length: cola }, (_, i) => total - cola + 1 + i),
    ];
  const w = max - 4; // ventana central
  const ini = actual - Math.floor(w / 2);
  return [
    1,
    null,
    ...Array.from({ length: w }, (_, i) => ini + i),
    null,
    total,
  ];
}

// ¿pantalla de celular? Se actualiza si girás o redimensionás
export function useMovil(consulta = "(max-width: 768px)") {
  const [movil, setMovil] = useState(() => window.matchMedia(consulta).matches);
  useEffect(() => {
    const q = window.matchMedia(consulta);
    const cambio = () => setMovil(q.matches);
    q.addEventListener("change", cambio);
    return () => q.removeEventListener("change", cambio);
  }, [consulta]);
  return movil;
}
