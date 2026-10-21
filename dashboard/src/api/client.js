const BASE_URL = import.meta.env.VITE_API_URL;

export async function get(ruta, params = {}) {
  const limpio = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== "" && v != null),
  );
  const qs = new URLSearchParams(limpio).toString();
  const res = await fetch(`${BASE_URL}${ruta}${qs ? `?${qs}` : ""}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

const cache = new Map();

export function getCacheado(ruta, params = {}) {
  const clave = ruta + JSON.stringify(params);
  if (!cache.has(clave)) {
    cache.set(
      clave,
      get(ruta, params).catch((e) => {
        cache.delete(clave);
        throw e;
      }),
    );
  }
  return cache.get(clave);
}
