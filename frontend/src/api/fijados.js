const BASE = "/api/v1";
const op = { credentials: "include" };
const ok = (r) => {
  if (!r.ok) throw new Error(`Error ${r.status}`);
  return r;
};

export const getFijados = (desde, hasta) =>
  fetch(`${BASE}/inicio/fijados?desde=${desde}&hasta=${hasta}`, op)
    .then(ok)
    .then((r) => r.json());

export const fijar = (id) =>
  fetch(`${BASE}/inicio/fijados/${id}`, { ...op, method: "PUT" }).then(ok);

export const desfijar = (id) =>
  fetch(`${BASE}/inicio/fijados/${id}`, { ...op, method: "DELETE" }).then(ok);

export const buscarRepuestos = (q, signal) =>
  fetch(`${BASE}/inicio/fijados/buscar?q=${encodeURIComponent(q)}`, {
    ...op,
    signal,
  })
    .then(ok)
    .then((r) => r.json());
