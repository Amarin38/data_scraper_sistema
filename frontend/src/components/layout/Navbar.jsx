import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import MenuUsuario from "./MenuUsuario.jsx";
import {
  inicio_ep,
  repuestos_ep,
  ficha_stock_ep,
  parque_movil_ep,
} from "../../constants.js";

const items = [
  { to: inicio_ep, label: "Inicio" },
  { to: repuestos_ep, label: "Repuestos" },
  { to: ficha_stock_ep, label: "Ficha Stock" },
  { to: parque_movil_ep, label: "Parque Movil" },
];

const norm = (s) => `/${String(s).replace(/^\/+/, "")}`;

export default function Navbar() {
  const [abierto, setAbierto] = useState(false);
  const [ind, setInd] = useState(null); // posición del indicador: { x, w }
  const [listo, setListo] = useState(false);
  const barra = useRef(null);
  const { pathname } = useLocation();
  const actual = items.find(
    (i) => pathname === norm(i.to) || pathname.startsWith(`${norm(i.to)}/`),
  );

  // se cierra al navegar
  useEffect(() => {
    setAbierto(false);
  }, [pathname]);

  // mide la pestaña actual para que el indicador se deslice hasta ella
  useLayoutEffect(() => {
    const el = barra.current;
    if (!el) return;
    const medir = () => {
      const tab = el.querySelector(".tab.activa");
      if (!tab || tab.offsetWidth === 0) return setInd(null); // celular: pestañas ocultas
      const b = el.getBoundingClientRect();
      const t = tab.getBoundingClientRect();
      setInd({ x: t.left - b.left, w: t.width });
    };
    medir();
    const ro = new ResizeObserver(medir);
    ro.observe(el);
    document.fonts?.ready.then(medir);
    return () => ro.disconnect();
  }, [pathname]);

  // la animación se activa recién después de la primera medida (si no, el indicador "viaja" desde el borde al cargar)
  useEffect(() => {
    if (ind) setListo(true);
  }, [ind]);

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
    <nav ref={barra} className={`navbar${abierto ? " menu-abierto" : ""}`}>
      {/* indicador deslizante de la pestaña actual (escritorio) */}
      <span
        className={`nav-indicador${ind ? " visible" : ""}${listo ? " listo" : ""}`}
        style={ind ? { "--x": `${ind.x}px`, "--w": `${ind.w}px` } : undefined}
        aria-hidden="true"
      />

      {/* botón de menú: solo se ve en el celular */}
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

      {/* marca: lleva a Inicio (en el celular queda solo el logo) */}
      <Link to={inicio_ep} className="nav-marca" aria-label="Ir a Inicio">
        <img className="nav-logo" src="/favicon.svg" alt="" />
        <span>Estadísticas Dota</span>
      </Link>

      {/* página actual: solo celular */}
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
