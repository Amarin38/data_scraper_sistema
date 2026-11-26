import { useRef, useState } from "react";
import { BLOQUES, NCOL } from "../../hooks/planificar.js";

const MIN_COLUMNAS = 2;
const UMBRAL = 5; // px que hay que mover para que sea un arrastre y no un clic
const BORDE_SCROLL = 70; // px del borde donde empieza el desplazamiento automático

const geometria = (grilla) => {
  const estilo = getComputedStyle(grilla);
  const columnas = estilo.gridTemplateColumns.split(" ").length;
  const sep = parseFloat(estilo.columnGap) || 0;
  const rect = grilla.getBoundingClientRect();
  const unidad = (rect.width - (columnas - 1) * sep) / columnas + sep;
  return { columnas, sep, unidad, rect };
};

const celdasDe = (grilla) =>
  [...grilla.children].filter((el) => el.classList.contains("celda"));

/* ---------- arrastre ----------
   Al empezar se mide una sola vez dónde está cada celda (en coordenadas de la grilla, que no cambian
   con el scroll). Durante el movimiento no se lee nada del DOM: el puntero solo escribe `translate`,
   y una vez por cuadro se recalcula el destino con los datos guardados. */

function preparar(a) {
  const g = geometria(a.grilla);
  a.g = g;
  a.gridTop0 = g.rect.top;
  a.gridLeft = g.rect.left;
  a.otras = celdasDe(a.grilla)
    .filter((el) => el !== a.celda)
    .map((el) => {
      const r = el.getBoundingClientRect();
      return {
        id: el.dataset.id,
        col: Number(el.dataset.col),
        span: Number(el.dataset.span),
        top: r.top - g.rect.top,
        alto: r.height,
      };
    });
  a.scrollNow = a.scroller.scrollTop;
}

function seguir(a) {
  const dx = a.px - a.x0;
  const dy = a.py - a.y0 + (a.scrollNow - a.scroll0);
  a.celda.style.translate = `${dx}px ${dy}px`;
}

// dónde caería la tarjeta si se suelta ahora: bloque, tarjeta de referencia y línea guía
function destinoDe(a) {
  const { unidad, sep } = a.g;
  const col = Math.min(
    NCOL - 1,
    Math.max(0, Math.floor((a.px - a.gridLeft) / unidad)),
  );
  const bloque = BLOQUES.findIndex(
    (b) => col + 1 >= b.inicio && col + 1 < b.inicio + b.ancho,
  );
  const b = BLOQUES[bloque];
  const fin = b.inicio + b.ancho - 1;
  const y = a.py - (a.gridTop0 - (a.scrollNow - a.scroll0)); // y dentro de la grilla

  const enBloque = a.otras
    .filter((o) => o.col <= fin && o.col + o.span - 1 >= b.inicio)
    .sort((p, q) => p.top - q.top);
  const antes = enBloque.find((o) => o.top + o.alto / 2 > y);
  const ultima = enBloque[enBloque.length - 1];

  return {
    bloque,
    antesId: antes ? antes.id : null,
    despuesId: !antes && ultima ? ultima.id : null,
    guia: {
      left: (b.inicio - 1) * unidad,
      top: antes ? antes.top - 6 : ultima ? ultima.top + ultima.alto + 6 : 0,
      width: b.ancho * unidad - sep,
    },
  };
}

function actualizarGuia(a) {
  a.destino = destinoDe(a);
  const { left, top, width } = a.destino.guia;
  a.guia.style.left = `${left}px`;
  a.guia.style.top = `${top}px`;
  a.guia.style.width = `${width}px`;
}

// un ciclo por cuadro: desplazamiento automático cerca de los bordes y actualización de la guía
function ciclo(a) {
  const paso = () => {
    if (!a.activo) return;
    const r = a.scroller.getBoundingClientRect();
    let v = 0;
    if (a.py < r.top + BORDE_SCROLL)
      v = -Math.ceil((r.top + BORDE_SCROLL - a.py) / 5);
    else if (a.py > r.bottom - BORDE_SCROLL)
      v = Math.ceil((a.py - (r.bottom - BORDE_SCROLL)) / 5);
    if (v) {
      a.scroller.scrollTop += Math.max(-25, Math.min(25, v));
      a.scrollNow = a.scroller.scrollTop;
      seguir(a);
      a.sucio = true;
    }
    if (a.sucio) {
      a.sucio = false;
      actualizarGuia(a);
    }
    a.raf = requestAnimationFrame(paso);
  };
  return paso;
}

/**
 * Celda de la grilla de Inicio: envuelve una tarjeta y, SOLO en modo edición, le agrega
 *  - dos manijas laterales para cambiar su ancho en columnas (doble clic: automático);
 *  - un asa en la parte superior para arrastrarla a otra columna o posición (Esc cancela);
 *  - un botón para quitar el panel.
 * `ancho` = columnas fijadas (undefined = automático); `bloque` = 0..2 si fue movida.
 * Fuera del modo edición la tarjeta no se puede mover ni redimensionar.
 */
export default function Celda({
  id,
  titulo,
  ancho,
  bloque,
  editando,
  onAncho,
  onMover,
  onQuitar,
  children,
}) {
  const ref = useRef(null);
  const redim = useRef(null);
  const mov = useRef(null);
  const [arrastrando, setArrastrando] = useState(false);

  /* ---------- ancho ---------- */
  const empezarAncho = (e, lado) => {
    const celda = ref.current;
    const g = geometria(celda.parentElement);
    if (g.columnas < 2) return; // en una sola columna no se redimensiona
    e.preventDefault();
    e.currentTarget.setPointerCapture(e.pointerId);
    const r = celda.getBoundingClientRect();
    redim.current = {
      lado,
      columnas: g.columnas,
      sep: g.sep,
      unidad: g.unidad,
      ancla: lado === "der" ? r.left : r.right, // borde que no se mueve
      ultimo: null,
    };
  };

  const moverAncho = (e) => {
    const a = redim.current;
    if (!a) return;
    const distancia =
      a.lado === "der" ? e.clientX - a.ancla : a.ancla - e.clientX;
    const span = Math.min(
      a.columnas,
      Math.max(MIN_COLUMNAS, Math.round((distancia + a.sep) / a.unidad)),
    );
    if (span !== a.ultimo) {
      a.ultimo = span;
      onAncho(id, span);
    }
  };

  /* ---------- mover ---------- */
  const cerrarMov = (cancelar) => {
    const a = mov.current;
    if (!a) return;
    mov.current = null;
    cancelAnimationFrame(a.raf);
    document.removeEventListener("keydown", a.tecla);
    a.scroller.removeEventListener("scroll", a.alScroll);
    document.body.style.userSelect = "";
    document.body.style.cursor = "";

    if (a.activo) {
      a.activo = false;
      a.guia?.remove();
      a.celda.style.translate = "";
      setArrastrando(false);
      if (!cancelar && a.destino) {
        const { bloque: destino, antesId, despuesId } = a.destino;
        onMover({
          id,
          bloque: destino,
          antesId,
          despuesId,
          snapshot: celdasDe(a.grilla).map((el) => ({
            id: el.dataset.id,
            col: Number(el.dataset.col),
            span: Number(el.dataset.span),
            top: el.offsetTop,
          })),
        });
      }
    }
  };

  const empezarMov = (e) => {
    if (e.button !== 0) return;
    const celda = ref.current;
    const grilla = celda.parentElement;
    if (geometria(grilla).columnas < 2) return; // una sola columna: sin arrastre
    e.currentTarget.setPointerCapture(e.pointerId);
    const scroller = celda.closest(".inicio") ?? document.scrollingElement;
    const a = {
      celda,
      grilla,
      scroller,
      x0: e.clientX,
      y0: e.clientY,
      px: e.clientX,
      py: e.clientY,
      scroll0: scroller.scrollTop,
      scrollNow: scroller.scrollTop,
      activo: false,
      sucio: false,
      guia: null,
      raf: 0,
      destino: null,
      tecla: (ev) => ev.key === "Escape" && cerrarMov(true),
      alScroll: () => {
        // scroll con la rueda durante el arrastre: la tarjeta sigue debajo del puntero
        if (!a.activo) return;
        a.scrollNow = scroller.scrollTop;
        seguir(a);
        a.sucio = true;
      },
    };
    mov.current = a;
    document.addEventListener("keydown", a.tecla);
    scroller.addEventListener("scroll", a.alScroll, { passive: true });
  };

  const moverMov = (e) => {
    const a = mov.current;
    if (!a) return;
    a.px = e.clientX;
    a.py = e.clientY;
    if (!a.activo) {
      if (Math.hypot(a.px - a.x0, a.py - a.y0) < UMBRAL) return;
      a.activo = true;
      preparar(a);
      a.guia = document.createElement("div");
      a.guia.className = "celda-destino";
      a.grilla.appendChild(a.guia);
      document.body.style.userSelect = "none";
      document.body.style.cursor = "grabbing";
      setArrastrando(true);
      a.raf = requestAnimationFrame(ciclo(a));
    }
    seguir(a); // solo escribe: la guía se recalcula una vez por cuadro
    a.sucio = true;
  };

  return (
    <div
      ref={ref}
      className={`celda${arrastrando ? " arrastrando" : ""}${editando ? " editando" : ""}`}
      data-id={id}
      data-ancho={ancho ?? ""}
      data-bloque={bloque ?? ""}
    >
      {children}
      {editando && (
        <>
          <button
            type="button"
            className="celda-quitar"
            aria-label={`Quitar ${titulo ?? "panel"}`}
            title="Quitar panel"
            onClick={() => onQuitar(id)}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.4"
              strokeLinecap="round"
              aria-hidden="true"
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
            Quitar
          </button>
          <span
            className="celda-asa"
            title="Arrastrá para mover la tarjeta"
            onPointerDown={empezarMov}
            onPointerMove={moverMov}
            onPointerUp={() => cerrarMov(false)}
            onPointerCancel={() => cerrarMov(true)}
          />
          {["izq", "der"].map((lado) => (
            <span
              key={lado}
              className={`celda-redim ${lado}`}
              role="separator"
              aria-orientation="vertical"
              title="Arrastrá para cambiar el ancho · doble clic: automático"
              onPointerDown={(e) => empezarAncho(e, lado)}
              onPointerMove={moverAncho}
              onPointerUp={() => (redim.current = null)}
              onPointerCancel={() => (redim.current = null)}
              onDoubleClick={() => onAncho(id, null)}
            />
          ))}
        </>
      )}
    </div>
  );
}
