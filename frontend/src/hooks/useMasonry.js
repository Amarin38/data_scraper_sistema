import { useLayoutEffect } from "react";
import { BLOQUES, NCOL, planificar } from "./planificar.js";

const FILA = 4; // px; debe coincidir con grid-auto-rows de .tarjetas

/**
 * Tablero masonry sobre la grilla CSS de `.tarjetas` (hijos: <Celda data-ancho="">).
 *  - Escritorio (8 columnas): tres bloques de 3, 3 y 2. Las celdas automáticas toman el ancho del
 *    bloque donde quedan más arriba; las de ancho fijo (data-ancho) lo conservan.
 *  - Una columna (tablet y celular): todas a lo ancho, una debajo de otra.
 * Cada celda se configura con data-ancho (columnas fijadas) y data-bloque (0..2 si el usuario la movió). El hook deja en cada celda data-col y data-span con su ubicación final.
 * `clave` cambia cuando cambia la configuración y fuerza el reacomodo.
 * La separación vertical sale de la variable CSS --gap-v del contenedor.
 */
export function useMasonry(ref, clave = "") {
  useLayoutEffect(() => {
    const cont = ref.current;
    if (!cont) return;

    const gap = () =>
      parseFloat(getComputedStyle(cont).getPropertyValue("--gap-v")) || 0;
    const filas = (el, g) => Math.ceil((el.offsetHeight + g) / FILA);
    const fijo = (el) => {
      const n = parseInt(el.dataset.ancho, 10);
      return n >= 1 && n <= NCOL ? n : null;
    };
    const bloque = (el) => {
      const n = parseInt(el.dataset.bloque, 10);
      return n >= 0 && n < BLOQUES.length ? n : null;
    };
    const celdasDe = () =>
      [...cont.children].filter((el) => el.classList.contains("celda"));

    const acomodar = () => {
      const g = gap();
      const celdas = celdasDe();
      const columnas =
        getComputedStyle(cont).gridTemplateColumns.split(" ").length;

      // una sola columna
      if (columnas < NCOL) {
        for (const el of celdas) {
          el.style.gridColumn = "1 / -1";
          el.style.gridRowStart = "auto";
          el.style.gridRowEnd = `span ${filas(el, g)}`;
        }
        return;
      }

      // el ancho cambia el alto: se mide, se planifica y se repite hasta que no cambie
      let anterior = "";
      for (let vuelta = 0; vuelta < 4; vuelta++) {
        for (const el of celdas) {
          if (!/span/.test(el.style.gridColumn)) {
            el.style.gridColumn = `1 / span ${fijo(el) ?? 4}`; // ancho provisional para medir
          }
        }
        const alturas = celdas.map((el) => filas(el, g));
        const plan = planificar(alturas, celdas.map(fijo), celdas.map(bloque));

        const firma = JSON.stringify([plan, alturas]);
        celdas.forEach((el, i) => {
          const p = plan[i];
          el.style.gridColumn = `${p.inicio} / span ${p.ancho}`;
          el.style.gridRowStart = String(p.fila + 1);
          el.style.gridRowEnd = `span ${alturas[i]}`;
          el.dataset.col = String(p.inicio);
          el.dataset.span = String(p.ancho);
        });
        if (firma === anterior) break;
        anterior = firma;
      }
    };

    const ro = new ResizeObserver(acomodar);
    const observar = () => {
      celdasDe().forEach((el) => ro.observe(el));
      acomodar();
    };

    ro.observe(cont);
    observar();
    const mo = new MutationObserver(observar);
    mo.observe(cont, { childList: true });

    return () => {
      ro.disconnect();
      mo.disconnect();
    };
  }, [ref, clave]);
}
