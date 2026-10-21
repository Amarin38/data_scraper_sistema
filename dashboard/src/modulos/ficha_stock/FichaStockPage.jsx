import { get, getCacheado } from "../../api/client.js";
import {
  ficha_stock_ep,
  cabeceras_ep,
  movimientos_ep,
} from "../../constants.js";
import { useState } from "react";
import Tabla from "../../components/grafico/Tabla.jsx";
import Filtros from "../../components/grafico/Filtros.jsx";

const getFicha = (filtros) => get(ficha_stock_ep, filtros);
const getCabeceras = () => getCacheado(cabeceras_ep);
const getMovimientos = () => getCacheado(movimientos_ep);

const hoy = () => new Date().toLocaleDateString("en-CA");

const filtros_ficha_stock = [
  {
    tipo: "select",
    campo: "deposito",
    etiqueta: "Todos los depositos",
    opciones: getCabeceras,
  },
  {
    tipo: "select",
    campo: "movimiento",
    etiqueta: "Todos los movimientos",
    opciones: getMovimientos,
  },
  {
    tipo: "texto",
    campo: "descripcion",
    placeholder: "Buscar descripcion...",
  },
  { tipo: "texto", campo: "codigo", placeholder: "Buscar código..." },
  {
    tipo: "fecha",
    campo: "fecha_desde",
    etiqueta: "Desde",
  },
  {
    tipo: "fecha",
    campo: "fecha_hasta",
    etiqueta: "Hasta",
    porDefecto: () => hoy(),
  },
];

export default function FichaStockPage() {
  const [filas, setFilas] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);
  const [filtros, setFiltros] = useState(null);

  const columnas_ficha = [
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
      titulo: "Fecha Movimiento",
      campo: "FechaMov",
      claveOrden: "FechaMov",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Cabecera",
      campo: "Deposito",
      claveOrden: "Deposito",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Movimiento",
      campo: "TipoMov",
      claveOrden: "TipoMov",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Cantidad",
      campo: "Cantidad",
      claveOrden: "Cantidad",
      tipo: "numeric",
      alinear: "centro",
    },
    {
      titulo: "Precio",
      campo: "PrecioUnitario",
      claveOrden: "PrecioUnitario",
      tipo: "numeric",
      alinear: "centro",
    },
    {
      titulo: "Interno",
      campo: "Interno",
      claveOrden: "Interno",
      tipo: "numeric",
      alinear: "centro",
    },

    {
      titulo: "Tipo Usuario",
      campo: "TipoUsuario",
      claveOrden: "TipoUsuario",
      tipo: "texto",
      alinear: "centro",
    },

    {
      titulo: "Transferencia",
      campo: "DepositoTransfer",
      claveOrden: "DepositoTransfer",
      tipo: "numeric",
      alinear: "centro",
    },
  ];

  return (
    <div className="pagina">
      <Filtros config={filtros_ficha_stock} onCambio={setFiltros} />
      <Tabla
        datosTabla={getFicha}
        columnas={columnas_ficha}
        filtros={filtros}
        ordenCol="FechaMov"
        pkFila="IDFichaStock"
        paginacion="cursor"
        seleccionada={seleccionado?.IDRepuesto}
        onSeleccionar={setSeleccionado}
      />
    </div>
  );
}
