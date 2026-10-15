export default function Paginacion({
  pagina,
  hayMas,
  onAnterior,
  onSiguiente,
}) {
  return (
    <div className="paginacion">
      <button disabled={pagina === 0} onClick={onAnterior}>
        ‹ Anterior
      </button>
      <span>Página {pagina + 1}</span>
      <button disabled={!hayMas} onClick={onSiguiente}>
        Siguiente ›
      </button>
    </div>
  );
}
