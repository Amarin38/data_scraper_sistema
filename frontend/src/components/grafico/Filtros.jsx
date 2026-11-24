import { useEffect, useMemo, useState } from "react";
import { get } from "../../api/client.js";
import { conjuntos_ep } from "../../constants.js";
import CampoFecha from "../CampoFecha.jsx";

function Campo({ titulo, clase = "", children }) {
  return (
    <label className={`filtro ${clase}`.trim()}>
      {titulo && <span className="filtro-titulo">{titulo}</span>}
      {children}
    </label>
  );
}

function errorNumero(f, valores) {
  if (f.tipo !== "numero") return null;
  const v = valores[f.campo];
  if (v === "") return null; // vacío: se repone al salir del campo
  const n = Number(v);
  if (n < 0) return "No negativo";
  if (f.max != null && n > f.max) return `Hasta ${f.max}`;
  if (f.menorOIgualQue) {
    const otro = valores[f.menorOIgualQue];
    if (otro !== "" && n > Number(otro)) return "Mayor que máx.";
  }
  if (f.mayorOIgualQue) {
    const otro = valores[f.mayorOIgualQue];
    if (otro !== "" && n < Number(otro)) return "Menor que mín.";
  }
  return null;
}

export default function Filtros({ config = [], onCambio }) {
  const [valores, setValores] = useState(() =>
    Object.fromEntries(
      config.map((f) => [
        f.campo,
        f.porDefecto ? f.porDefecto() : f.tipo === "check" ? false : "",
      ]),
    ),
  );

  const [opciones, setOpciones] = useState({});
  const [abierto, setAbierto] = useState(false);

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

  const hayError = config.some((f) => errorNumero(f, valores));

  useEffect(() => {
    if (!hayError) onCambio(limpio);
  }, [limpio, hayError, onCambio]);

  const poner = (campo, valor) => setValores((v) => ({ ...v, [campo]: valor }));

  // cantidad de filtros que difieren de su valor por defecto
  const activos = config.filter((f) => {
    const def = f.porDefecto ? f.porDefecto() : f.tipo === "check" ? false : "";
    return String(valores[f.campo] ?? "") !== String(def ?? "");
  }).length;

  // agrupa por `grupo` y, dentro de cada grupo, apila los "check" consecutivos
  const grupos = useMemo(() => {
    const out = [];
    for (const f of config) {
      const clave = f.grupo ?? "";
      let g = out.find((x) => x.clave === clave);
      if (!g) out.push((g = { clave, items: [] }));
      const ult = g.items[g.items.length - 1];
      if (f.tipo !== "check") g.items.push(f);
      else if (ult?.tipo === "checks") ult.lista.push(f);
      else g.items.push({ tipo: "checks", campo: f.campo, lista: [f] });
    }
    return out;
  }, [config]);

  return (
    <div className={`filtros${abierto ? " abierto" : ""}`}>
      {/* botón para desplegar los filtros: solo se ve en el celular */}
      <button
        type="button"
        className="filtros-toggle"
        onClick={() => setAbierto((a) => !a)}
        aria-expanded={abierto}
      >
        <span>Filtros{activos > 0 && ` (${activos})`}</span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M3 6l5 5 5-5" />
        </svg>
      </button>

      {grupos.map((g) => (
        <div
          key={g.clave}
          className={`filtros-grupo${g.clave ? " filtros-grupo-der" : ""}`}
        >
          {g.items.map((f) => {
            if (f.tipo === "opciones")
              return (
                <Campo key={f.campo} titulo={f.etiqueta}>
                  <select
                    value={valores[f.campo]}
                    onChange={(e) => poner(f.campo, e.target.value)}
                  >
                    {f.lista.map(([valor, texto]) => (
                      <option key={valor} value={valor}>
                        {texto}
                      </option>
                    ))}
                  </select>
                </Campo>
              );
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
                <CampoFecha
                  key={f.campo}
                  titulo={f.etiqueta}
                  valor={valores[f.campo]}
                  min={f.desde}
                  alinear="derecha"
                  onCommit={(v) => poner(f.campo, v)}
                />
              );
            if (f.tipo === "checks")
              return (
                <div key={f.campo} className="checks-filtro">
                  {f.lista.map((c) => (
                    <label key={c.campo} className="check-filtro">
                      <input
                        type="checkbox"
                        checked={valores[c.campo]}
                        onChange={(e) => poner(c.campo, e.target.checked)}
                      />
                      {c.etiqueta}
                    </label>
                  ))}
                </div>
              );
            if (f.tipo === "numero") {
              const error = errorNumero(f, valores);
              const paso = (delta) => {
                let n =
                  Math.round((Number(valores[f.campo] || 0) + delta) * 10) / 10;
                if (n < 0) n = 0;
                if (f.max != null && n > f.max) n = f.max;
                poner(f.campo, String(n));
              };
              return (
                <Campo key={f.campo} titulo={f.etiqueta} clase="filtro-num">
                  <div
                    className="num-caja"
                    aria-invalid={error ? "true" : undefined}
                  >
                    <input
                      type="number"
                      min="0"
                      max={f.max}
                      step="0.5"
                      value={valores[f.campo]}
                      onChange={(e) => poner(f.campo, e.target.value)}
                      onBlur={() => {
                        if (valores[f.campo] === "" && f.porDefecto)
                          poner(f.campo, f.porDefecto());
                      }}
                    />
                    <div className="num-pasos">
                      <button
                        type="button"
                        tabIndex={-1}
                        aria-label="Subir"
                        onClick={() => paso(0.5)}
                      >
                        <svg
                          width="8"
                          height="8"
                          viewBox="0 0 8 8"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.6"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M1 5.5 4 2.5 7 5.5" />
                        </svg>
                      </button>
                      <button
                        type="button"
                        tabIndex={-1}
                        aria-label="Bajar"
                        onClick={() => paso(-0.5)}
                      >
                        <svg
                          width="8"
                          height="8"
                          viewBox="0 0 8 8"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.6"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M1 2.5 4 5.5 7 2.5" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  {error && <span className="campo-error">{error}</span>}
                </Campo>
              );
            }
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
      ))}
    </div>
  );
}
