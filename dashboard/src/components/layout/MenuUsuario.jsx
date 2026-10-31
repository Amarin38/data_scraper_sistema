import { useEffect, useRef, useState } from "react";
import { useAuth } from "../../auth/AuthContext.jsx";

const icono = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

export default function MenuUsuario() {
  const { usuario, logout, cambiarModoNoche } = useAuth();
  const [abierto, setAbierto] = useState(false);
  const raiz = useRef(null);

  // se cierra con un toque afuera o con Escape
  useEffect(() => {
    if (!abierto) return;
    const fuera = (e) => !raiz.current?.contains(e.target) && setAbierto(false);
    const tecla = (e) => e.key === "Escape" && setAbierto(false);
    document.addEventListener("pointerdown", fuera);
    document.addEventListener("keydown", tecla);
    return () => {
      document.removeEventListener("pointerdown", fuera);
      document.removeEventListener("keydown", tecla);
    };
  }, [abierto]);

  const user = usuario?.user;
  const tipo = usuario?.tipo;
  const noche = !!usuario?.modo_noche;

  return (
    <div className={`navbar-usuario ${tipo}`} ref={raiz}>
      <button
        type="button"
        className="usuario-disparador"
        aria-haspopup="menu"
        aria-expanded={abierto}
        onClick={() => setAbierto((a) => !a)}
      >
        <span className="usuario-identidad">
          <span className="usuario-avatar" aria-hidden="true">
            <svg viewBox="0 0 30 30" width="30" height="30">
              <text
                x="15"
                y="15"
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="14"
                fontWeight="700"
                fill="#fff"
              >
                {user?.[0]?.toUpperCase()}
              </text>
            </svg>
          </span>
        </span>
        <svg
          className="usuario-flecha"
          width="12"
          height="12"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M3 6l5 5 5-5" />
        </svg>
      </button>

      {abierto && (
        <div className="usuario-menu" role="menu">
          <div className="usuario-menu-cab">
            <span className="usuario-menu-nombre">{user}</span>
            <span className="usuario-menu-rol">{tipo}</span>
          </div>

          <button
            type="button"
            className="usuario-menu-item"
            role="menuitemcheckbox"
            aria-checked={noche}
            onClick={() => cambiarModoNoche(!noche)}
          >
            <svg {...icono}>
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
            </svg>
            <span className="usuario-menu-texto">Modo noche</span>
            <span className="interruptor" aria-hidden="true" />
          </button>

          <div className="usuario-menu-sep" />

          <button
            type="button"
            className="usuario-menu-item salir"
            role="menuitem"
            onClick={logout}
          >
            <svg {...icono}>
              <path d="M14 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
              <path d="M10 17l5-5-5-5" />
              <path d="M15 12H3" />
            </svg>
            <span className="usuario-menu-texto">Cerrar sesión</span>
          </button>
        </div>
      )}
    </div>
  );
}
