import { useState } from "react";
import { get, getCacheado } from "../api/client.js";
import {
  existencia_stock_ep,
  conjuntos_ep,
  existencia_stock_exportar_ep,
  fmt_num,
  fmt_fecha,
} from "../constants.js";
import Tabla from "../components/grafico/Tabla.jsx";
import Filtros from "../components/grafico/Filtros.jsx";

const mesesAFecha = (n) => {
  const d = new Date();
  d.setDate(1);
  d.setMonth(d.getMonth() - Number(n));
  const mes = String(d.getMonth() + 1).padStart(2, "0");
  return `${d.getFullYear()}-${mes}-01`;
};

const getExistencias = ({ meses_demanda, ...filtros }) =>
  get(existencia_stock_ep, {
    ...filtros,
    demanda_desde: meses_demanda ? mesesAFecha(meses_demanda) : "",
  });
const getConjuntos = () => getCacheado(conjuntos_ep);

const exportar = {
  ruta: existencia_stock_exportar_ep,
  nombre: "existencia_stock",
};

const filtros_existencia_stock = [
  {
    tipo: "texto",
    campo: "descripcion",
    etiqueta: "Descripción",
    placeholder: "Buscar...",
  },
  {
    tipo: "texto",
    campo: "codigo",
    etiqueta: "Código",
    placeholder: "Buscar...",
  },
  {
    tipo: "select",
    campo: "conjunto",
    etiqueta: "Conjunto",
    placeholder: "Todos",
    opciones: getConjuntos,
  },
  {
    tipo: "numero",
    campo: "meses_min",
    etiqueta: "Mínimo (meses)",
    porDefecto: () => "1",
    max: 64,
    menorOIgualQue: "meses_max",
  },
  {
    tipo: "numero",
    campo: "meses_max",
    etiqueta: "Máximo (meses)",
    porDefecto: () => "2",
    max: 64,
    mayorOIgualQue: "meses_min",
  },
  {
    tipo: "opciones",
    campo: "meses_demanda",
    etiqueta: "Demanda de los últimos",
    porDefecto: () => "12",
    lista: [
      ["3", "3 meses"],
      ["6", "6 meses"],
      ["12", "12 meses"],
    ],
  },
  {
    tipo: "check",
    campo: "solo_con_minmax",
    etiqueta: "Solo con mínimo y máximo",
  },
];

const celda = (v) => (v == null ? "—" : fmt_num.format(v));

export default function ExistenciaStockPage() {
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
      render: (f) => fmt_fecha(f.FechaExistencia),
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
    {
      titulo: "Mínimo",
      campo: "Minimo",
      claveOrden: "Minimo",
      tipo: "numeric",
      alinear: "centro",
      render: (f) => celda(f.Minimo),
    },
    {
      titulo: "Máximo",
      campo: "Maximo",
      claveOrden: "Maximo",
      tipo: "numeric",
      alinear: "centro",
      render: (f) => celda(f.Maximo),
    },
    {
      titulo: "Reponer",
      campo: "Reponer",
      claveOrden: "Reponer",
      tipo: "numeric",
      alinear: "centro",
      render: (f) =>
        f.Reponer == null ? (
          "—"
        ) : (
          <span className={Number(f.Reponer) > 0 ? "neg" : ""}>
            {fmt_num.format(f.Reponer)}
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
          claseFila={(f) => (Number(f.Reponer) > 0 ? "alerta" : "")}
          seleccionada={seleccionado?.IDRepuesto}
          onSeleccionar={setSeleccionado}
          exportar={exportar}
          ordenServidor
        />
      </div>
    </div>
  );
}
