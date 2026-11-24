import { filaClickeable } from "./filaClickeable.js";

// Lista corta de repuestos: código en pastilla + descripción (hasta 2 líneas).
// Usa <ul> a propósito: `.tarjeta-grafico > div` estira cualquier div hijo (position: absolute !important).
export default function ListaCompacta({
  filas,
  codigo = "Codigo",
  descripcion = "Descripcion",
  max = 5,
  vacioTexto = "Sin elementos",
  onSeleccionar,
  seleccionado,
}) {
  const lista = Array.isArray(filas) ? filas : [];
  if (!lista.length)
    return (
      <ul className="lista-compacta">
        <li className="lc-vacio">{vacioTexto}</li>
      </ul>
    );

  const visibles = lista.slice(0, max);
  const resto = lista.length - visibles.length;

  return (
    <ul className="lista-compacta">
      {visibles.map((f) => (
        <li
          key={f.IDRepuesto ?? f[codigo]}
          title={f[descripcion]}
          className={`${onSeleccionar ? "clickeable" : ""}${f.IDRepuesto === seleccionado ? " sel" : ""}`.trim()}
          {...filaClickeable(f, onSeleccionar)}
        >
          <b className="lc-codigo">{f[codigo]}</b>
          <span className="lc-texto">{f[descripcion]}</span>
        </li>
      ))}
      {resto > 0 && <li className="lc-mas">+{resto} más</li>}
    </ul>
  );
}
