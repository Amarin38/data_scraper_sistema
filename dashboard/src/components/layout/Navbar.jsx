import { NavLink } from "react-router-dom";
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

export default function Navbar() {
  return (
    <nav className="navbar">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) => (isActive ? "tab activa" : "tab")}
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
