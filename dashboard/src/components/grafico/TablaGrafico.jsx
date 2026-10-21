import { useState } from "react";
import Filtros from "./Filtros.jsx";
import Tabla from "./Tabla.jsx";
import PanelLateral from "./PanelLateral.jsx";

export default function TablaGrafico({
  datosTabla,
  vistas,
  subtitulo,
  columnas,
  ordenCol,
  pkFila,
  filtrosConfig,
}) {
  const [seleccionado, setSeleccionado] = useState(null);
  const [filtros, setFiltros] = useState(null); // null = Filtros todavía no avisó

  return (
    <div className="pagina">
      <Filtros config={filtrosConfig} onCambio={setFiltros} />
      <div className={`contenido${seleccionado ? " con-panel" : ""}`}>
        <Tabla
          datosTabla={datosTabla}
          columnas={columnas}
          filtros={filtros}
          ordenCol={ordenCol}
          pkFila={pkFila}
          paginacion="offset"
          seleccionado={seleccionado?.[pkFila]}
          onSeleccionar={setSeleccionado}
        />
        <PanelLateral
          vistas={vistas}
          subtitulo={subtitulo}
          seleccionado={seleccionado}
          setSeleccionado={setSeleccionado}
        />
      </div>
    </div>
  );
}
