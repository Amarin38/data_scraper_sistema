import { useEffect, useMemo, useState } from "react";
import { get } from "../../api/client.js";
import { conjuntos_ep } from "../../constants.js";

function Campo({ titulo, children }) {
  return (
    <label className="filtro">
      {titulo && <span className="filtro-titulo">{titulo}</span>}
      {children}
    </label>
  );
}

export default function Filtros({ config, onCambio }) {
  const [valores, setValores] = useState(() =>
    Object.fromEntries(
      config.map((f) => [
        f.campo,
        f.porDefecto ? f.porDefecto() : f.tipo === "check" ? false : "",
      ]),
    ),
  );

  const [opciones, setOpciones] = useState({});

  useEffect(() => {
    config
      .filter((f) => f.tipo === "select")
      .forEach((f) =>
        f
          .opciones()
          .then((o) => setOpciones((p) => ({ ...p, [f.campo]: o })))
          .catch(console.error),
      );
  }, [config]);

  const limpio = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(valores).map(([k, v]) => [k, v === false ? "" : v]),
      ),
    [valores],
  );

  useEffect(() => {
    onCambio(limpio);
  }, [limpio, onCambio]);

  const poner = (campo, valor) => setValores((v) => ({ ...v, [campo]: valor }));

  return (
    <div className="filtros">
      {config.map((f) => {
        if (f.tipo === "select")
          return (
            <Campo key={f.campo} titulo={f.etiqueta}>
              <select
                value={valores[f.campo]}
                onChange={(e) => poner(f.campo, e.target.value)}
              >
                <option value="">{f.placeholder ?? "Todos"}</option>
                {(opciones[f.campo] ?? []).map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
            </Campo>
          );
        if (f.tipo === "fecha")
          return (
            <Campo key={f.campo} titulo={f.etiqueta}>
              <input
                type="date"
                value={valores[f.campo]}
                onChange={(e) => poner(f.campo, e.target.value)}
              />
            </Campo>
          );
        if (f.tipo === "check")
          return (
            <label key={f.campo} className="check-filtro">
              <input
                type="checkbox"
                checked={valores[f.campo]}
                onChange={(e) => poner(f.campo, e.target.checked)}
              />
              {f.etiqueta}
            </label>
          );
        return (
          <Campo key={f.campo} titulo={f.etiqueta}>
            <input
              value={valores[f.campo]}
              placeholder={f.placeholder}
              onChange={(e) => poner(f.campo, e.target.value)}
            />
          </Campo>
        );
      })}
    </div>
  );
}
