const BASE_URL = import.meta.env.VITE_API_URL;

// 401 en cualquier ruta de datos => la sesión venció
function sesionVencida(res, ruta) {
  if (res.status === 401 && !ruta.startsWith("/auth/")) {
    window.dispatchEvent(new Event("sesion-expirada"));
  }
}

export async function get(ruta, params = {}) {
  const limpio = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== "" && v != null),
  );
  const qs = new URLSearchParams(limpio).toString();
  const res = await fetch(`${BASE_URL}${ruta}${qs ? `?${qs}` : ""}`);

  sesionVencida(res, ruta);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  return res.json();
}

export async function post(ruta, cuerpo) {
  const res = await fetch(`${BASE_URL}${ruta}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  const datos = await res.json().catch(() => null);
  if (!res.ok) {
    const d = datos?.detail;
    throw new Error(typeof d === "string" ? d : `HTTP ${res.status}`);
  }
  return datos;
}

const cache = new Map();

export function limpiarCache() {
  cache.clear();
}

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
  sesionVencida(res, ruta);
  if (!res.ok) {
    const cuerpo = await res.json().catch(() => null);
    throw new Error(cuerpo?.detail ?? `HTTP ${res.status}`);
  }
  return res;
}
