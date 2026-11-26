// Planificador del tablero de Inicio (función pura, sin DOM).
//
// Grilla de NCOL columnas dividida en bloques base: 3 + 3 + 2.
// Cada tarjeta, en orden:
//  - automática: va al bloque donde queda más arriba y toma su ancho (empate: el de más a la izquierda);
//  - de ancho fijo (w): va a la posición de la grilla donde queda más arriba, conservando w;
//  - con bloque forzado (índice 0..2, porque el usuario la movió): va a ese bloque; si además tiene
//    ancho fijo, arranca en el borde izquierdo del bloque.
// Devuelve, por tarjeta, { inicio (columna 1..NCOL), ancho, fila (0 = arriba) }.
// Las alturas y las filas están en filas de la grilla (ya incluyen la separación vertical).

export const BLOQUES = [
  { inicio: 1, ancho: 3 },
  { inicio: 4, ancho: 3 },
  { inicio: 7, ancho: 2 },
];
export const NCOL = BLOQUES.reduce((n, b) => n + b.ancho, 0);

// bloque al que pertenece una columna (1..NCOL)
export const bloqueDe = (col) => {
  const i = BLOQUES.findIndex(
    (b) => col >= b.inicio && col < b.inicio + b.ancho,
  );
  return i < 0 ? 0 : i;
};

export function planificar(alturas, fijos, bloques = []) {
  const col = new Array(NCOL).fill(0);

  return alturas.map((alto, i) => {
    const w = fijos[i];
    const forzado = bloques[i];
    let opciones;
    if (forzado != null && BLOQUES[forzado]) {
      const b = BLOQUES[forzado];
      opciones = [
        {
          inicio: w ? Math.min(b.inicio, NCOL - w + 1) : b.inicio,
          ancho: w ?? b.ancho,
        },
      ];
    } else if (w) {
      opciones = Array.from({ length: NCOL - w + 1 }, (_, k) => ({
        inicio: k + 1,
        ancho: w,
      }));
    } else {
      opciones = BLOQUES;
    }

    let mejor = null;
    for (const o of opciones) {
      const fila = Math.max(...col.slice(o.inicio - 1, o.inicio - 1 + o.ancho));
      if (!mejor || fila < mejor.fila) mejor = { ...o, fila }; // empate: gana la de más a la izquierda
    }
    for (let c = mejor.inicio - 1; c < mejor.inicio - 1 + mejor.ancho; c++) {
      col[c] = mejor.fila + alto;
    }
    return mejor;
  });
}
