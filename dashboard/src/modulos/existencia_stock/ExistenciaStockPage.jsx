import { get, getCacheado } from "../../api/client.js";
import { existencia_stock_ep, conjuntos_ep } from "../../constants.js";
import { useState } from "react";
import Tabla from "../../components/grafico/Tabla.jsx";
import Filtros from "../../components/grafico/Filtros.jsx";
import { fmt_num, fecha_hoy } from "../../constants.js";

const getExistencias = (filtros) => get(existencia_stock_ep, filtros);
const getConjuntos = () => getCacheado(conjuntos_ep);

const filtros_existencia_stock = [
  { tipo: "select", campo: "conjunto", opciones: getConjuntos },
  {
    tipo: "texto",
    campo: "descripcion",
    placeholder: "Buscar descripcion...",
  },
  { tipo: "texto", campo: "codigo", placeholder: "Buscar código..." },
];

export default function ExistenciaStockPage() {
  const [filas, setFilas] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);
  const [filtros, setFiltros] = useState(null);

  const columnas_existencias = [
    {
      titulo: "Codigo",
      campo: "Codigo",
      claveOrden: "Codigo",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Repuesto",
      campo: "Descripcion",
      claveOrden: "Descripcion",
      tipo: "texto",
      alinear: "izquierda",
    },
    {
      titulo: "Fecha",
      campo: "FechaExistencia",
      claveOrden: "FechaExistencia",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Stock",
      campo: "Stock",
      claveOrden: "Stock",
      tipo: "numeric",
      alinear: "centro",
      render: (f) => (
        <span className={Number(f.Stock) <= 0 ? "neg" : "pos"}>
          {fmt_num.format(f.Stock)}
        </span>
      ),
    },
  ];

  return (
    <div className="pagina">
      <Filtros config={filtros_existencia_stock} onCambio={setFiltros} />
      <div className="contenido">
        <Tabla
          datosTabla={getExistencias}
          columnas={columnas_existencias}
          filtros={filtros}
          ordenCol="Descripcion"
          pkFila="IDExistencia"
          paginacion="offset"
          seleccionada={seleccionado?.IDRepuesto}
          onSeleccionar={setSeleccionado}
        />
      </div>
    </div>
  );
}
