// opciones = [{ id, etiqueta }]; valor = id seleccionado; onCambio(id)
// Toma el color de --acento-tarjeta si está dentro de una tarjeta; si no, usa el violeta por defecto.
export default function SelectorPildoras({
  opciones,
  valor,
  onCambio,
  etiqueta = "Selector",
}) {
  return (
    <div className="selector-pildoras" role="group" aria-label={etiqueta}>
      {opciones.map((o) => (
        <button
          key={o.id}
          type="button"
          className={o.id === valor ? "activo" : ""}
          aria-pressed={o.id === valor}
          onClick={() => onCambio(o.id)}
        >
          {o.etiqueta}
        </button>
      ))}
    </div>
  );
}
