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

export function urlApi(ruta, params) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(
      ([, v]) => v !== "" && v != null && v !== false,
    ),
  );
  return `${BASE_URL}${ruta}?${qs}`;
}

export async function abrirStream(ruta, params, signal) {
  const res = await fetch(urlApi(ruta, params), { signal });
  if (!res.ok) {
    const cuerpo = await res.json().catch(() => null);
    throw new Error(cuerpo?.detail ?? `HTTP ${res.status}`);
  }
  return res;
}
