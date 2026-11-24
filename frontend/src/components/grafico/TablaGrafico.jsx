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
  ordenDir,
  pkFila,
  claseFila,
  filtrosConfig,
  exportar,
  ordenServidor = false,
  panelAbierto,
}) {
  const [seleccionado, setSeleccionado] = useState(null);
  const [filtros, setFiltros] = useState(null);

  return (
    <div className="pagina">
      <Filtros config={filtrosConfig} onCambio={setFiltros} />
      <div className={`contenido${seleccionado ? " con-panel" : ""}`}>
        <Tabla
          datosTabla={datosTabla}
          columnas={columnas}
          filtros={filtros}
          ordenCol={ordenCol}
          ordenDir={ordenDir}
          pkFila={pkFila}
          claseFila={claseFila}
          paginacion="offset"
          seleccionado={seleccionado?.[pkFila]}
          panelAbierto={!!seleccionado}
          onSeleccionar={setSeleccionado}
          exportar={exportar}
          ordenServidor={ordenServidor}
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
