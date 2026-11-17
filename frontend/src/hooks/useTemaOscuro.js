import { useState, useEffect } from "react";

export function useTemaOscuro() {
  const leer = () =>
    document.documentElement.getAttribute("data-tema") === "oscuro";
  const [oscuro, setOscuro] = useState(leer);
  useEffect(() => {
    const obs = new MutationObserver(() => setOscuro(leer()));
    obs.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-tema"],
    });
    return () => obs.disconnect();
  }, []);
  return oscuro;
}
