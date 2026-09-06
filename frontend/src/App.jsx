import "./App.css";
import { useState, useEffect } from "react";

function Fila({ familia, articulo, descripcion }) {
  return (
    <tr>
      <td class="cell center" contenteditable="false">{familia}</td>
      <td class="cell center" contenteditable="false">{articulo}</td>
      <td class="cell center" contenteditable="false">{descripcion}</td>
    </tr>
  );
}

function Repuestos() {
  const [repuestos, setRepuestos] = useState([]);

  useEffect(() => {
    fetch("/api/v1/repuestos")
      .then((res) => res.json())
      .then(setRepuestos);
  }, []);

  return (
    <div class="spreadsheet-container">
      <table class="sheet-table">
        <thead>
          <tr>
            <th scope="col">Familia</th>
            <th scope="col">Articulo</th>
            <th scope="col">Descripcion</th>
          </tr>
        </thead>
        <tbody>
          {repuestos.map((r) => (
            <Fila
              key={r.IDRepuesto}
              familia={r.Familia}
              articulo={r.Articulo}
              descripcion={r.Descripcion}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  return (
    <>
      <h1>Prueba</h1>
      <Repuestos />
    </>
  );
}
export default App;
