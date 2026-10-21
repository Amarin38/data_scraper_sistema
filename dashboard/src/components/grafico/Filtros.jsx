import { useEffect, useMemo, useState } from "react";
import { get } from "../../api/client.js";
import { conjuntos_ep } from "../../constants.js";

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
            <select
              key={f.campo}
              value={valores[f.campo]}
              onChange={(e) => poner(f.campo, e.target.value)}
            >
              <option value="">{f.etiqueta ?? "Todos"}</option>
              {(opciones[f.campo] ?? []).map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          );
        if (f.tipo === "fecha")
          return (
            <label key={f.campo} className="fecha-filtro">
              {f.etiqueta}
              <input
                type="date"
                value={valores[f.campo]}
                onChange={(e) => poner(f.campo, e.target.value)}
              />
            </label>
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
          <input
            key={f.campo}
            value={valores[f.campo]}
            placeholder={f.placeholder}
            onChange={(e) => poner(f.campo, e.target.value)}
          />
        );
      })}
    </div>
  );
}
