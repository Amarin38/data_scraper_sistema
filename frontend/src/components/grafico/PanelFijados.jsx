import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import TarjetaRanking from "./TarjetaRanking.jsx";
import { fmt_spark, fmt_dinero, fmt_dinero_corto } from "../../constants.js";
import {
  buscarRepuestos,
  desfijar,
  fijar,
  getFijados,
} from "../../api/fijados.js";

const COLUMNAS = [
  {
    campo: "Consumo",
    titulo: "Consumo",
    ancho: "64px",
    formatoTitulo: (v) => fmt_spark.format(Number(v)),
  },
  {
    campo: "Gasto", // última columna: de acá sale el total del encabezado
    titulo: "Gasto",
    ancho: "120px",
    destacada: true,
    formatoTitulo: (v) => fmt_dinero_corto.format(Number(v)),
    formatoLista: (v) => fmt_dinero.format(Number(v)),
  },
];

// Períodos en años calendario, siempre relativos al año actual
const periodosDe = (anio) => [
  { id: "previos", desde: anio - 2, hasta: anio - 1 },
  { id: "previo-actual", desde: anio - 1, hasta: anio },
  { id: "tres", desde: anio - 2, hasta: anio },
];

const textoAnios = (desde, hasta) => {
  const a = Array.from({ length: hasta - desde + 1 }, (_, i) => desde + i);
  return a.length > 2
    ? `${a.slice(0, -1).join(", ")} y ${a.at(-1)}`
    : a.join("–");
};

function SelectorFijados({ fijados, onAlternar }) {
  const [abierto, setAbierto] = useState(false);
  const [pos, setPos] = useState(null);
  const [q, setQ] = useState("");
  const [res, setRes] = useState([]);
  const [fallo, setFallo] = useState(false);
  const btn = useRef(null);
  const pop = useRef(null);

  const cerrar = useCallback(() => {
    setAbierto(false);
    setQ("");
    setRes([]);
  }, []);

  const abrir = () => {
    const r = btn.current.getBoundingClientRect();
    const ancho = Math.min(340, window.innerWidth * 0.86);
    const left = Math.max(
      8,
      Math.min(r.right - ancho, window.innerWidth - ancho - 8),
    );
    setPos({ top: r.bottom + 6, left });
    setAbierto(true);
  };

  useEffect(() => {
    if (!abierto || q.trim().length < 2) return;
    const ctl = new AbortController();
    const t = setTimeout(
      () =>
        buscarRepuestos(q.trim(), ctl.signal)
          .then((r) => {
            setRes(r);
            setFallo(false);
          })
          .catch((e) => e.name !== "AbortError" && setFallo(true)),
      300,
    );
    return () => {
      clearTimeout(t);
      ctl.abort();
    };
  }, [q, abierto]);

  useEffect(() => {
    if (!abierto) return;
    const fuera = (e) => {
      if (!pop.current?.contains(e.target) && !btn.current?.contains(e.target))
        cerrar();
    };
    const tecla = (e) => e.key === "Escape" && cerrar();
    const scroll = (e) => !pop.current?.contains(e.target) && cerrar();
    document.addEventListener("mousedown", fuera);
    document.addEventListener("keydown", tecla);
    window.addEventListener("resize", cerrar);
    window.addEventListener("scroll", scroll, true);
    return () => {
      document.removeEventListener("mousedown", fuera);
      document.removeEventListener("keydown", tecla);
      window.removeEventListener("resize", cerrar);
      window.removeEventListener("scroll", scroll, true);
    };
  }, [abierto, cerrar]);

  const ids = new Set(fijados.map((f) => f.IDRepuesto));
  const buscando = q.trim().length >= 2;
  const lista = buscando ? res : fijados;

  return (
    <>
      <button
        ref={btn}
        type="button"
        className="fijados-btn"
        onClick={abierto ? cerrar : abrir}
        aria-expanded={abierto}
        aria-label="Agregar o quitar repuestos fijados"
        title="Agregar o quitar repuestos"
      >
        +
      </button>
      {abierto &&
        createPortal(
          <div
            ref={pop}
            className="fijados-pop"
            style={{ top: pos.top, left: pos.left }}
          >
            <input
              type="search"
              autoFocus
              placeholder="Buscar repuesto…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
            <ul>
              {lista.map((r) => (
                <li key={r.IDRepuesto}>
                  <label>
                    <input
                      type="checkbox"
                      checked={ids.has(r.IDRepuesto)}
                      onChange={() =>
                        onAlternar(r.IDRepuesto, ids.has(r.IDRepuesto))
                      }
                    />
                    <span>
                      {r.Codigo} · {r.Descripcion}
                    </span>
                  </label>
                </li>
              ))}
              {!lista.length && (
                <li className="fijados-vacio">
                  {!buscando
                    ? "Escribí para buscar"
                    : fallo
                      ? "No se pudo buscar"
                      : "Sin resultados"}
                </li>
              )}
            </ul>
          </div>,
          document.body,
        )}
    </>
  );
}

export default function PanelFijados({ onSeleccionar, seleccionado }) {
  const anio = new Date().getFullYear();
  const periodos = periodosDe(anio);
  const [datos, setDatos] = useState([]); // una lista de filas por período
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const cargar = useCallback(
    () =>
      Promise.all(periodosDe(anio).map((p) => getFijados(p.desde, p.hasta)))
        .then((r) => {
          setDatos(r);
          setError(null);
        })
        .catch((e) =>
          setError(e.message ?? "No se pudieron cargar los fijados"),
        )
        .finally(() => setCargando(false)),
    [anio],
  );

  useEffect(() => {
    cargar();
  }, [cargar]);

  const alternar = async (id, estaFijado) => {
    try {
      await (estaFijado ? desfijar(id) : fijar(id));
    } finally {
      await cargar();
    }
  };

  const opciones = periodos.map((p, i) => {
    const filas = datos[i] ?? [];
    return {
      id: p.id,
      etiqueta: `${p.desde}–${p.hasta}`,
      titulo: `Repuestos fijados (${textoAnios(p.desde, p.hasta)})`,
      filas,
      valor: filas.length ? undefined : "—",
      detalle: !filas.length
        ? "Usá + para fijar repuestos"
        : p.hasta === anio
          ? `Gasto total · ${anio} hasta hoy`
          : "Gasto total",
    };
  });

  return (
    <TarjetaRanking
      opciones={opciones}
      etiquetaSelector="Período"
      columnas={COLUMNAS}
      color="#15803d"
      accionesTitulo={
        <SelectorFijados fijados={datos[0] ?? []} onAlternar={alternar} />
      }
      cols={3}
      posicion={false}
      onSeleccionar={onSeleccionar}
      seleccionado={seleccionado}
      cargando={cargando}
      error={error}
    />
  );
}
