export default function Pestana({
  items,
  activa,
  onCambiar,
  clase = "tab",
  children,
}) {
  return (
    <nav className="panel-tabs">
      {items.map((it) => (
        <button
          key={it}
          className={it === activa ? `${clase} activa` : clase}
          onClick={() => onCambiar(it)}
        >
          {it}
        </button>
      ))}
      {children}
    </nav>
  );
}
