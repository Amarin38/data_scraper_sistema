import PanelLateralDetalle from "./PanelLateralDetalle.jsx";

export default function PanelLateral({
  vistas,
  subtitulo,
  seleccionado,
  setSeleccionado,
}) {
  // Arrastre del divisor: ancho del panel = distancia del mouse al borde derecho del libro
  function empezarArrastre(e) {
    e.preventDefault();
    const contenido = e.currentTarget.closest(".contenido"); // el libro, sin ref
    const caja = contenido.getBoundingClientRect();
    contenido.classList.add("arrastrando"); // apaga la transición mientras arrastrás

    function mover(ev) {
      const nuevo = caja.right - ev.clientX;
      // mínimo 300px para el panel y 300px para la tabla
      const limitado = Math.min(Math.max(nuevo, 300), caja.width - 300);
      contenido.style.setProperty("--ancho-panel", `${limitado}px`);
    }
    function soltar() {
      contenido.classList.remove("arrastrando");
      window.removeEventListener("pointermove", mover);
      window.removeEventListener("pointerup", soltar);
    }
    window.addEventListener("pointermove", mover);
    window.addEventListener("pointerup", soltar);
  }

  return (
    <aside className="panel">
      {seleccionado && (
        <div className="divisor" onPointerDown={empezarArrastre} />
      )}
      <div className="panel-interior">
        {seleccionado && (
          <PanelLateralDetalle
            vistas={vistas}
            repuesto={seleccionado}
            subtitulo={subtitulo}
            onCerrar={() => setSeleccionado(null)}
          />
        )}
      </div>
    </aside>
  );
}
