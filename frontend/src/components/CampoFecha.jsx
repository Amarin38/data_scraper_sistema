import { useEffect, useRef, useState } from "react";
import { DayPicker } from "react-day-picker";
import { es } from "react-day-picker/locale";
import "react-day-picker/style.css";

const ANCHO_POPUP = 330; // ancho aproximado del calendario con su padding

const pad = (n) => String(n).padStart(2, "0");
const aTexto = (d) =>
  `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const aDate = (s) => {
  if (!s) return undefined;
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
};
const mostrar = (s) => s.split("-").reverse().join("/");
const hoyLocal = () => aTexto(new Date());

// "12032022" -> "12/03/2022" mientras se escribe
const mascara = (s) => {
  const d = s.replace(/\D/g, "").slice(0, 8);
  if (d.length <= 2) return d;
  if (d.length <= 4) return `${d.slice(0, 2)}/${d.slice(2)}`;
  return `${d.slice(0, 2)}/${d.slice(2, 4)}/${d.slice(4)}`;
};

// "dd/mm/aaaa" -> "aaaa-mm-dd", o null si no es un día real (ej. 31/02)
const parsear = (t) => {
  const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(t);
  if (!m) return null;
  const [, d, mes, a] = m;
  const f = new Date(Number(a), Number(mes) - 1, Number(d));
  const ok =
    f.getFullYear() === Number(a) &&
    f.getMonth() === Number(mes) - 1 &&
    f.getDate() === Number(d);
  return ok ? `${a}-${mes}-${d}` : null;
};

export default function CampoFecha({
  titulo,
  valor,
  min,
  max,
  alinear = "izquierda",
  onCommit,
}) {
  const [abierto, setAbierto] = useState(false);
  const [texto, setTexto] = useState(valor ? mostrar(valor) : "");
  const [error, setError] = useState(null);
  const ref = useRef(null);
  const [lado, setLado] = useState(alinear);

  // al abrir, mide el lugar disponible y elige de qué lado desplegar
  function alternar() {
    if (!abierto) {
      const r = ref.current.getBoundingClientRect();
      const cabe = {
        izquierda: r.left + ANCHO_POPUP <= window.innerWidth,
        derecha: r.right - ANCHO_POPUP >= 0,
      };
      const otro = alinear === "izquierda" ? "derecha" : "izquierda";
      setLado(cabe[alinear] ? alinear : cabe[otro] ? otro : "izquierda");
    }
    setAbierto((a) => !a);
  }

  // si el valor cambia desde afuera (otro repuesto, calendario), se resincroniza
  useEffect(() => {
    setTexto(valor ? mostrar(valor) : "");
    setError(null);
  }, [valor]);

  // cierra el calendario al hacer clic afuera o con Escape
  useEffect(() => {
    if (!abierto) return;
    const fuera = (e) => !ref.current?.contains(e.target) && setAbierto(false);
    const tecla = (e) => e.key === "Escape" && setAbierto(false);
    document.addEventListener("mousedown", fuera);
    document.addEventListener("keydown", tecla);
    return () => {
      document.removeEventListener("mousedown", fuera);
      document.removeEventListener("keydown", tecla);
    };
  }, [abierto]);

  function validar(t, alSalir) {
    if (t === "") {
      setError(null);
      onCommit(""); // borrado: sin filtro
      return;
    }
    if (t.length < 10) {
      // incompleta: mientras escribe no molesta; al salir del campo, avisa
      setError(alSalir ? "Formato: dd/mm/aaaa" : null);
      return;
    }
    const iso = parsear(t);
    if (!iso) setError("Fecha inválida");
    else if (Number(iso.slice(0, 4)) < 1990) setError("Desde 1990");
    else if (iso > hoyLocal()) setError("Posterior a hoy");
    else if (min && iso < min) setError("Anterior a «desde»");
    else if (max && iso > max) setError("Posterior a «hasta»");
    else {
      setError(null);
      onCommit(iso);
    }
  }

  const tope = max && max < hoyLocal() ? max : hoyLocal();
  const deshabilitados = [
    { after: aDate(tope) },
    ...(min ? [{ before: aDate(min) }] : []),
  ];

  return (
    <div className="kpi selector-fecha" ref={ref}>
      <span className="kpi-titulo">{titulo}</span>

      <div className="campo-ancla">
        <div className="fecha-caja" aria-invalid={error ? "true" : undefined}>
          <input
            type="text"
            inputMode="numeric"
            placeholder="dd/mm/aaaa"
            maxLength={10}
            value={texto}
            onChange={(e) => {
              const t = mascara(e.target.value);
              setTexto(t);
              if (t === "" || t.length === 10) validar(t, false);
              else setError(null);
            }}
            onBlur={(e) => {
              // si el foco pasa al calendario, no se valida todavía
              if (ref.current?.contains(e.relatedTarget)) return;
              validar(texto, true);
            }}
            onKeyDown={(e) => e.key === "Enter" && validar(texto, true)}
          />
          <button
            type="button"
            aria-label="Abrir calendario"
            aria-expanded={abierto}
            onClick={alternar}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <rect x="2" y="3" width="12" height="11" rx="2" />
              <path d="M2 7h12M5 1.5v3M11 1.5v3" />
            </svg>
          </button>
        </div>

        {error && <span className="campo-error">{error}</span>}
      </div>

      {abierto && (
        <div className={`selector-popup ${lado}`}>
          <DayPicker
            mode="single"
            locale={es}
            captionLayout="dropdown"
            startMonth={new Date(1990, 0)}
            endMonth={new Date()}
            defaultMonth={aDate(valor) ?? aDate(tope)}
            selected={aDate(valor)}
            disabled={deshabilitados}
            onSelect={(d) => {
              setError(null);
              onCommit(d ? aTexto(d) : "");
              setAbierto(false);
            }}
          />
          {valor && (
            <button
              type="button"
              className="selector-limpiar"
              onClick={() => {
                setError(null);
                onCommit("");
                setAbierto(false);
              }}
            >
              Limpiar
            </button>
          )}
        </div>
      )}
    </div>
  );
}
