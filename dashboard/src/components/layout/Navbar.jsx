import { NavLink } from "react-router-dom";
import { indices_ep, previsiones_ep, duraciones_ep } from "../../constants.js";

const items = [
  { to: indices_ep, label: "Índices de Consumo" },
  { to: previsiones_ep, label: "Previsiones" },
  { to: duraciones_ep, label: "Duracion Repuestos" },
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
