import { useCallback, useEffect, useState } from "react";
import { bloqueDe } from "./planificar.js";

const CLAVE = "inicio.tablero";
const VACIO = { anchos: {}, orden: [], bloques: {}, visibles: null };

// versiones anteriores guardaban "izq" | "der"; ahora es el índice del bloque (0..2)
const migrar = (bloques = {}) =>
  Object.fromEntries(
    Object.entries(bloques).map(([id, b]) => [
      id,
      b === "izq" ? 0 : b === "der" ? 1 : b,
    ]),
  );

const leer = () => {
  try {
    const t = { ...VACIO, ...JSON.parse(localStorage.getItem(CLAVE)) };
    return { ...t, bloques: migrar(t.bloques) };
  } catch {
    return VACIO;
  }
};

const sin = (obj, id) => {
  const copia = { ...obj };
  delete copia[id];
  return copia;
};

/**
 * Disposición personalizada de las tarjetas de Inicio, guardada en este navegador:
 *  - visibles: ids de los paneles mostrados (null = los de `porDefecto`);
 *  - anchos:   { id: columnas } solo de los que el usuario redimensionó;
 *  - orden:    ids de arriba hacia abajo (vacío = orden de `visibles`);
 *  - bloques:  { id: 0 | 1 | 2 } columna de cada tarjeta, una vez que el usuario movió alguna.
 * Un panel recién agregado entra sin ancho ni bloque: el masonry lo ubica y lo dimensiona solo.
 */
export function useTablero(porDefecto) {
  const [tablero, setTablero] = useState(leer);

  useEffect(() => {
    try {
      localStorage.setItem(CLAVE, JSON.stringify(tablero));
    } catch {
      /* sin almacenamiento: queda solo en memoria */
    }
  }, [tablero]);

  const visibles = (tablero.visibles ?? porDefecto).filter((id) =>
    porDefecto.includes(id),
  );

  const fijarAncho = useCallback((id, columnas) => {
    setTablero((t) => ({
      ...t,
      anchos:
        columnas == null ? sin(t.anchos, id) : { ...t.anchos, [id]: columnas },
    }));
  }, []);

  // `snapshot` es la ubicación actual de todas las celdas: al mover una, el resto queda fijo donde estaba
  const mover = useCallback(({ id, bloque, antesId, despuesId, snapshot }) => {
    setTablero((t) => {
      const visual = [...snapshot].sort(
        (a, b) => a.top - b.top || a.col - b.col,
      );
      const bloques = {};
      for (const s of visual) bloques[s.id] = bloqueDe(s.col);
      bloques[id] = bloque;

      const orden = visual.map((s) => s.id).filter((x) => x !== id);
      let pos = orden.length;
      if (antesId) pos = orden.indexOf(antesId);
      else if (despuesId) pos = orden.indexOf(despuesId) + 1;
      if (pos < 0) pos = orden.length;
      orden.splice(pos, 0, id);

      return { ...t, orden, bloques };
    });
  }, []);

  const agregar = useCallback(
    (id) => {
      setTablero((t) => {
        const vis = t.visibles ?? porDefecto;
        if (vis.includes(id)) return t;
        return {
          ...t,
          visibles: [...vis, id],
          anchos: sin(t.anchos, id),
          bloques: sin(t.bloques, id),
          orden: t.orden.filter((x) => x !== id),
        };
      });
    },
    [porDefecto],
  );

  const quitar = useCallback(
    (id) => {
      setTablero((t) => ({
        ...t,
        visibles: (t.visibles ?? porDefecto).filter((x) => x !== id),
        anchos: sin(t.anchos, id),
        bloques: sin(t.bloques, id),
        orden: t.orden.filter((x) => x !== id),
      }));
    },
    [porDefecto],
  );

  // vuelve al reparto y los anchos automáticos; conserva qué paneles están visibles
  const restablecer = useCallback(
    () => setTablero((t) => ({ ...VACIO, visibles: t.visibles })),
    [],
  );

  const personalizado =
    tablero.orden.length > 0 ||
    Object.keys(tablero.anchos).length > 0 ||
    Object.keys(tablero.bloques).length > 0;

  // orden final: el que guardó el usuario y, al final, los visibles que todavía no figuran
  const ids = [
    ...tablero.orden.filter((id) => visibles.includes(id)),
    ...visibles.filter((id) => !tablero.orden.includes(id)),
  ];

  return {
    ids,
    anchos: tablero.anchos,
    bloques: tablero.bloques,
    fijarAncho,
    mover,
    agregar,
    quitar,
    restablecer,
    personalizado,
  };
}
