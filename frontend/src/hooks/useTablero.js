import { useCallback, useEffect, useRef, useState } from "react";
import { get, put } from "../api/client.js";
import { preferencias_inicio_ep } from "../constants.js";
import { bloqueDe } from "./planificar.js";

// permitidos: ids de paneles autorizados para este usuario (null = todavía no se sabe)
const VACIO = {
  anchos: {},
  orden: [],
  bloques: {},
  visibles: null,
  permitidos: null,
};

const sin = (obj, id) => {
  const copia = { ...obj };
  delete copia[id];
  return copia;
};

const acotar = (n, min, max) =>
  Number.isFinite(n) ? Math.min(max, Math.max(min, n)) : undefined;

// estado del hook -> documento del servidor { v, Paneles: { id: {Visible, Ancho, Bloque, Orden} } }
// null en Ancho/Bloque/Orden = automático. Se incluyen los paneles por defecto aunque estén ocultos,
// para distinguir "el usuario lo quitó" de "panel nuevo del catálogo".
const aServidor = (t, porDefecto) => {
  const vis = t.visibles ?? porDefecto;
  const ids = new Set([
    ...porDefecto,
    ...vis,
    ...t.orden,
    ...Object.keys(t.anchos),
    ...Object.keys(t.bloques),
  ]);
  const Paneles = {};
  for (const id of ids) {
    if (t.permitidos && !t.permitidos.includes(id)) continue;
    const pos = t.orden.indexOf(id);
    Paneles[id] = {
      Visible: vis.includes(id),
      Ancho: t.anchos[id] ?? null,
      Bloque: t.bloques[id] ?? null,
      Orden: pos >= 0 ? pos : null,
    };
  }
  return { v: 1, Paneles };
};

// documento del servidor -> estado del hook. Acota valores (el catálogo pudo cambiar)
// y suma los paneles por defecto que todavía no figuran en el documento.
const desdeServidor = ({ Paneles = {}, Permitidos = [] }, porDefecto) => {
  const ok = (id) => Permitidos.includes(id);
  const ids = Object.keys(Paneles).filter(ok);
  if (ids.length === 0) return { ...VACIO, permitidos: Permitidos };

  const nuevos = porDefecto.filter((id) => ok(id) && !(id in Paneles));
  const anchos = {};
  const bloques = {};
  for (const id of ids) {
    const a = acotar(Paneles[id].Ancho, 2, 8);
    const b = acotar(Paneles[id].Bloque, 0, 2);
    if (a !== undefined) anchos[id] = a;
    if (b !== undefined) bloques[id] = b;
  }
  return {
    anchos,
    bloques,
    orden: ids
      .filter((id) => Number.isFinite(Paneles[id].Orden))
      .sort((a, b) => Paneles[a].Orden - Paneles[b].Orden),
    visibles: ids.filter((id) => Paneles[id].Visible !== false).concat(nuevos),
    permitidos: Permitidos,
  };
};

/**
 * Disposición personalizada de las tarjetas de Inicio, guardada por usuario en el servidor:
 *  - visibles: ids de los paneles mostrados (null = los de `porDefecto`);
 *  - anchos:   { id: columnas } solo de los que el usuario redimensionó;
 *  - orden:    ids de arriba hacia abajo (vacío = orden de `visibles`);
 *  - bloques:  { id: 0 | 1 | 2 } columna de cada tarjeta, una vez que el usuario movió alguna;
 *  - permitidos: paneles que el rol del usuario puede ver (lo decide el backend; acá solo se muestra).
 * Hasta que llega la respuesta del servidor (`listo` = false) `ids` es vacío: así no se muestran
 * ni se piden datos de paneles que después resultan ocultos o no permitidos.
 * Un panel recién agregado entra sin ancho ni bloque: el masonry lo ubica y lo dimensiona solo.
 */
export function useTablero(porDefecto) {
  const [tablero, setTablero] = useState(VACIO);
  const [listo, setListo] = useState(false); // ya se puede mostrar el tablero
  const [cargado, setCargado] = useState(false); // se cargó del servidor: recién ahí se puede guardar
  const defRef = useRef(porDefecto);
  defRef.current = porDefecto;
  const base = useRef(null); // último estado sincronizado con el servidor: { estado, texto }

  // carga inicial desde el servidor
  useEffect(() => {
    let vivo = true;
    get(preferencias_inicio_ep)
      .then((data) => {
        if (!vivo) return;
        const nuevo = desdeServidor(data, defRef.current);
        base.current = {
          estado: nuevo,
          texto: JSON.stringify(aServidor(nuevo, defRef.current)),
        };
        setTablero(nuevo);
        setCargado(true);
        setListo(true);
      })
      .catch(() => {
        // sin servidor: se muestra el reparto por defecto y no se guarda, para no pisar lo que haya allá
        if (vivo) setListo(true);
      });
    return () => {
      vivo = false;
    };
  }, []);

  // guardado con debounce; solo si el documento cambió respecto del último sincronizado
  // guarda el borrador actual; devuelve true si quedó sincronizado
  const guardar = useCallback(async () => {
    if (!cargado) return true;
    const cuerpo = aServidor(tablero, defRef.current);
    const texto = JSON.stringify(cuerpo);
    if (texto === base.current.texto) return true;
    try {
      await put(preferencias_inicio_ep, cuerpo);
      base.current = { estado: tablero, texto };
      return true;
    } catch {
      return false;
    }
  }, [tablero, cargado]);

  // vuelve a lo último guardado
  const descartar = useCallback(() => {
    if (base.current) setTablero(base.current.estado);
  }, []);

  const permitido = (id) =>
    tablero.permitidos == null || tablero.permitidos.includes(id);

  const visibles = (tablero.visibles ?? porDefecto).filter(
    (id) => porDefecto.includes(id) && permitido(id),
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
        if (t.permitidos && !t.permitidos.includes(id)) return t;
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
    () =>
      setTablero((t) => ({
        ...VACIO,
        visibles: t.visibles,
        permitidos: t.permitidos,
      })),
    [],
  );

  const personalizado =
    tablero.orden.length > 0 ||
    Object.keys(tablero.anchos).length > 0 ||
    Object.keys(tablero.bloques).length > 0;

  // orden final: el que guardó el usuario y, al final, los visibles que todavía no figuran
  const ids = listo
    ? [
        ...tablero.orden.filter((id) => visibles.includes(id)),
        ...visibles.filter((id) => !tablero.orden.includes(id)),
      ]
    : [];

  return {
    listo,
    ids,
    anchos: tablero.anchos,
    bloques: tablero.bloques,
    permitidos: tablero.permitidos,
    fijarAncho,
    mover,
    agregar,
    quitar,
    restablecer,
    personalizado,
    guardar,
    descartar,
  };
}
