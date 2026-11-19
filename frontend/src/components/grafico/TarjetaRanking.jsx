import { useState } from "react";
import TarjetaMicro from "./TarjetaMicro.jsx";
import ListaRanking from "./ListaRanking.jsx";
import SelectorPildoras from "./SelectorPildoras.jsx";

// Uso simple: <TarjetaRanking titulo filas columnas ... />
// Con selector: opciones={[{ id, etiqueta, ...cambios }]}, donde `cambios` pisa cualquier
// prop de la tarjeta (titulo, filas, columnas, color, valor, detalle, textoSuma...).
export default function TarjetaRanking({
  opciones,
  opcionInicial,
  etiquetaSelector,
  ...base
}) {
  const [sel, setSel] = useState(opcionInicial ?? opciones?.[0]?.id);
  const actual = opciones?.find((o) => o.id === sel) ?? opciones?.[0] ?? {};
  const { id: _id, etiqueta: _etiqueta, ...cambios } = actual;

  const {
    titulo,
    filas,
    codigo = "Codigo",
    descripcion = "Descripcion",
    columnas,
    barra,
    color = "#3b82f6",
    cols = 2,
    cargando,
    error,
    valor, // si lo pasás, reemplaza al valor grande
    detalle, // si lo pasás, reemplaza al texto de abajo
    sumar = true, // true: el valor grande es la suma de la última columna
    textoSuma, // texto bajo el valor grande cuando se suma
    tituloLista,
    posicion = true,
    acento,
    acciones, // nodo propio entre el detalle y la lista (se ignora si hay opciones)
  } = { ...base, ...cambios };

  const acentoReal = acento ?? color;
  const lista = Array.isArray(filas) ? filas : [];
  const primero = lista[0];
  const principal = columnas[columnas.length - 1];
  const fmtTitulo =
    principal.formatoTitulo ??
    principal.formatoLista ??
    principal.formato ??
    ((v) => v);
  const total = lista.reduce(
    (acc, f) => acc + Number(f[principal.campo] || 0),
    0,
  );

  const selector = opciones?.length ? (
    <SelectorPildoras
      opciones={opciones}
      valor={actual.id}
      onCambio={setSel}
      etiqueta={etiquetaSelector ?? titulo}
    />
  ) : (
    acciones
  );

  return (
    <TarjetaMicro
      titulo={titulo}
      cols={cols}
      acento={acentoReal}
      acciones={selector}
      valor={
        valor ??
        (sumar
          ? fmtTitulo(total)
          : primero
            ? fmtTitulo(primero[principal.campo])
            : "—")
      }
      detalle={
        detalle !== undefined
          ? detalle
          : sumar
            ? (textoSuma ?? `Suma de los ${lista.length} primeros`)
            : primero
              ? [primero[codigo], primero[descripcion]]
                  .filter(Boolean)
                  .join(" · ")
              : null
      }
      cargando={cargando}
      error={error}
      vacio={!cargando && lista.length === 0}
    >
      <ListaRanking
        filas={lista}
        codigo={codigo}
        descripcion={descripcion}
        columnas={columnas}
        barra={barra}
        color={color}
        titulo={tituloLista}
        posicion={posicion}
      />
    </TarjetaMicro>
  );
}
