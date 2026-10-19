import { NavLink } from "react-router-dom";
import { repuestos_ep } from "../../constants.js";

const items = [{ to: repuestos_ep, label: "Repuestos" }];

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
