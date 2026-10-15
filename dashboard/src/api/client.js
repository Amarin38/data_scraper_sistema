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
