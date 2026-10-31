import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import MenuUsuario from "./MenuUsuario.jsx";
import {
  inicio_ep,
  repuestos_ep,
  ficha_stock_ep,
  existencia_stock_ep,
  parque_movil_ep,
} from "../../constants.js";

const items = [
  { to: inicio_ep, label: "Inicio" },
  { to: repuestos_ep, label: "Repuestos" },
  { to: ficha_stock_ep, label: "Ficha Stock" },
  { to: existencia_stock_ep, label: "Existencia Stock" },
  { to: parque_movil_ep, label: "Parque Movil" },
];

const norm = (s) => `/${String(s).replace(/^\/+/, "")}`;

export default function Navbar() {
  const [abierto, setAbierto] = useState(false);
  const { pathname } = useLocation();
  const actual = items.find(
    (i) => pathname === norm(i.to) || pathname.startsWith(`${norm(i.to)}/`),
  );

  // se cierra al navegar
  useEffect(() => {
    setAbierto(false);
  }, [pathname]);

  // se cierra con Escape o con un toque en la barra fuera del menú
  useEffect(() => {
    if (!abierto) return;
    const fuera = (e) => {
      if (!e.target.closest(".nav-tabs, .nav-burger, .nav-fondo"))
        setAbierto(false);
    };
    const tecla = (e) => e.key === "Escape" && setAbierto(false);
    document.addEventListener("pointerdown", fuera);
    document.addEventListener("keydown", tecla);
    return () => {
      document.removeEventListener("pointerdown", fuera);
      document.removeEventListener("keydown", tecla);
    };
  }, [abierto]);

  return (
    <nav className={`navbar${abierto ? " menu-abierto" : ""}`}>
      {/* botón de menú y página actual: solo se ven en el celular */}
      <button
        type="button"
        className="nav-burger"
        aria-label="Menú"
        aria-expanded={abierto}
        aria-controls="nav-tabs"
        onClick={() => setAbierto((a) => !a)}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          {abierto ? (
            <path d="M6 6l12 12M18 6L6 18" />
          ) : (
            <path d="M4 7h16M4 12h16M4 17h16" />
          )}
        </svg>
      </button>
      <span className="nav-actual">{actual?.label ?? "Menú"}</span>

      {/* en escritorio este contenedor no existe (display: contents); en el celular es el panel */}
      <div id="nav-tabs" className="nav-tabs" onClick={() => setAbierto(false)}>
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => (isActive ? "tab activa" : "tab")}
          >
            {item.label}
          </NavLink>
        ))}
      </div>

      {abierto && (
        <div className="nav-fondo" onClick={() => setAbierto(false)} />
      )}

      <MenuUsuario />
    </nav>
  );
}
