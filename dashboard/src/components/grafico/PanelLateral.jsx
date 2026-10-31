import { useEffect, useState } from "react";
import PanelLateralDetalle from "./PanelLateralDetalle.jsx";

const MS_CIERRE = 450; // tiene que coincidir con --t-panel (0.45s)

export default function PanelLateral({
  vistas,
  subtitulo,
  seleccionado,
  setSeleccionado,
}) {
  // al cerrar, se conserva el último repuesto hasta que el panel termina de bajar
  const [ultimo, setUltimo] = useState(seleccionado);
  useEffect(() => {
    if (seleccionado) {
      setUltimo(seleccionado);
      return;
    }
    const t = setTimeout(() => setUltimo(null), MS_CIERRE);
    return () => clearTimeout(t);
  }, [seleccionado]);
  const mostrado = seleccionado ?? ultimo;

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
    <>
      {/* fondo para tocar afuera y cerrar: solo se ve en el celular (display: none en escritorio) */}
      {mostrado && (
        <div
          className={`panel-fondo${seleccionado ? " visible" : ""}`}
          onClick={() => setSeleccionado(null)}
          aria-hidden="true"
        />
      )}
      <aside className="panel">
        {mostrado && (
          <div className="divisor" onPointerDown={empezarArrastre} />
        )}
        <div className="panel-interior">
          {mostrado && (
            <PanelLateralDetalle
              vistas={vistas}
              repuesto={mostrado}
              subtitulo={subtitulo}
              onCerrar={() => setSeleccionado(null)}
            />
          )}
        </div>
      </aside>
    </>
  );
}
