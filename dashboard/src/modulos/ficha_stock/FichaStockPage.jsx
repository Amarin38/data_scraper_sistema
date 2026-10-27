import { get, getCacheado } from "../../api/client.js";
import {
  ficha_stock_ep,
  cabeceras_ep,
  movimientos_ep,
  ficha_stock_exportar_ep,
} from "../../constants.js";
import { useState } from "react";
import Tabla from "../../components/grafico/Tabla.jsx";
import Filtros from "../../components/grafico/Filtros.jsx";
import { fmt_num, fmt_fecha, fecha_hoy } from "../../constants.js";

const getFicha = (filtros) => get(ficha_stock_ep, filtros);
const getCabeceras = () => getCacheado(cabeceras_ep);
const getMovimientos = () => getCacheado(movimientos_ep);

const exportar = { ruta: ficha_stock_exportar_ep, nombre: "ficha_stock" };

const filtros_ficha_stock = [
  {
    tipo: "fecha",
    campo: "fecha_desde",
    etiqueta: "Desde",
  },
  {
    tipo: "fecha",
    campo: "fecha_hasta",
    etiqueta: "Hasta",
    porDefecto: () => fecha_hoy(),
  },
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
    campo: "deposito",
    etiqueta: "Cabecera",
    placeholder: "Todos",
    opciones: getCabeceras,
  },
  {
    tipo: "select",
    campo: "movimiento",
    etiqueta: "Movimientos",
    placeholder: "Todos",
    opciones: getMovimientos,
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
      render: (f) => fmt_fecha(f.FechaMov),
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
      render: (f) => (
        <span
          className={`badge ${f.TipoMov === "Entrada" ? "ok" : f.TipoMov === "Salida" ? "mal" : "neutro"}`}
        >
          {f.TipoMov}
        </span>
      ),
    },
    {
      titulo: "Cantidad",
      campo: "Cantidad",
      claveOrden: "Cantidad",
      tipo: "numeric",
      alinear: "centro",
      render: (f) => (
        <span className={Number(f.Cantidad) < 0 ? "neg" : "pos"}>
          {fmt_num.format(f.Cantidad)}
        </span>
      ),
    },
    {
      titulo: "Precio",
      campo: "PrecioUnitario",
      claveOrden: "PrecioUnitario",
      tipo: "numeric",
      alinear: "centro",
      render: (f) =>
        f.PrecioUnitario != null ? fmt_num.format(f.PrecioUnitario) : null,
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
      <div className="contenido">
        <Tabla
          datosTabla={getFicha}
          columnas={columnas_ficha}
          filtros={filtros}
          ordenCol="FechaMov"
          pkFila="IDFichaStock"
          paginacion="cursor"
          seleccionada={seleccionado?.IDRepuesto}
          onSeleccionar={setSeleccionado}
          exportar={exportar}
        />
      </div>
    </div>
  );
}
