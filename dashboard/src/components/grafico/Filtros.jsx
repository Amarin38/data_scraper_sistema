import { useEffect, useState } from "react";
import { get } from "../../api/client.js";
import { conjuntos_ep } from "../../constants.js";
import SelectConjuntos from "../SelectConjuntos.jsx";

export const getConjuntos = () => get(conjuntos_ep);

export default function Filtros({ onCambio, reset }) {
  const [conjunto, setConjunto] = useState("");
  const [conjuntos, setConjuntos] = useState([]);
  const [descripcion, setDescripcion] = useState("");
  const [codigo, setCodigo] = useState("");
  const [critico, setCritico] = useState(false);

  useEffect(() => {
    getConjuntos().then(setConjuntos).catch(console.error);
  }, []);

  useEffect(() => {
    onCambio({ conjunto, descripcion, codigo, critico: critico ? true : "" });
  }, [conjunto, descripcion, codigo, critico, onCambio]);

  function cambiarConjunto(conj) {
    setConjunto(conj);
    reset();
  }

  function cambiarDescripcion(desc) {
    setDescripcion(desc);
    reset();
  }

  function cambiarCodigo(cod) {
    setCodigo(cod);
    reset();
  }

  function cambiarCritico(valor) {
    setCritico(valor);
    reset();
  }

  return (
    <div className="filtros">
      <SelectConjuntos
        conjuntos={conjuntos}
        conjunto={conjunto}
        setConjunto={cambiarConjunto}
      />
      <input
        value={descripcion}
        onChange={(e) => cambiarDescripcion(e.target.value)}
        placeholder="Buscar descripcion..."
      />
      <input
        value={codigo}
        onChange={(e) => cambiarCodigo(e.target.value)}
        placeholder="Buscar código..."
      />
      <label className="check-filtro">
        <input
          type="checkbox"
          checked={critico}
          onChange={(e) => cambiarCritico(e.target.checked)}
        />
        Solo críticos
      </label>
    </div>
  );
}
