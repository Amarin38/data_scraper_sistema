import { get, getCacheado } from "../api/client.js";
import {
  parque_movil_hist_ep,
  carrocerias_ep,
  chasis_marcas_ep,
  chasis_modelos_ep,
  motor_marcas_ep,
  motor_modelos_ep,
  parque_movil_exportar_ep,
} from "../constants.js";
import { useState } from "react";
import Tabla from "../components/grafico/Tabla.jsx";
import Filtros from "../components/grafico/Filtros.jsx";
import { fmt_num, fmt_fecha, fecha_hoy } from "../constants.js";

const getParqueMovil = (filtros) => get(parque_movil_hist_ep, filtros);
const getCarrocerias = () => getCacheado(carrocerias_ep);
const getChasisMarcas = () => getCacheado(chasis_marcas_ep);
const getChasisModelos = () => getCacheado(chasis_modelos_ep);
const getMotorMarcas = () => getCacheado(motor_marcas_ep);
const getMotorModelos = () => getCacheado(motor_modelos_ep);

const exportar = { ruta: parque_movil_exportar_ep, nombre: "parque_movil" };

const filtros_parque_movil = [
  { tipo: "fecha", campo: "fecha_desde", etiqueta: "Desde" },
  {
    tipo: "fecha",
    campo: "fecha_hasta",
    etiqueta: "Hasta",
    porDefecto: () => fecha_hoy(),
  },
  {
    tipo: "texto",
    campo: "linea",
    etiqueta: "Línea",
    placeholder: "Buscar...",
  },
  {
    tipo: "texto",
    campo: "interno",
    etiqueta: "Interno",
    placeholder: "Buscar...",
  },
  {
    tipo: "texto",
    campo: "dominio",
    etiqueta: "Dominio",
    placeholder: "Buscar...",
  },
  {
    tipo: "select",
    campo: "carroceria",
    etiqueta: "Carroceria",
    placeholder: "Todas",
    opciones: getCarrocerias,
  },
  {
    tipo: "select",
    campo: "chasis_marca",
    etiqueta: "Marca Chasis",
    placeholder: "Todas",
    opciones: getChasisMarcas,
  },
  {
    tipo: "select",
    campo: "chasis_modelo",
    etiqueta: "Modelo Chasis",
    placeholder: "Todos",
    opciones: getChasisModelos,
  },
  {
    tipo: "select",
    campo: "motor_marca",
    etiqueta: "Marca Motor",
    placeholder: "Todas",
    opciones: getMotorMarcas,
  },
  {
    tipo: "select",
    campo: "motor_modelo",
    etiqueta: "Modelo Motor",
    placeholder: "Todos",
    opciones: getMotorModelos,
  },
];

export default function ParqueMovilPage() {
  const [filas, setFilas] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);
  const [filtros, setFiltros] = useState(null);

  const columnas_parque_movil = [
    {
      titulo: "Fecha",
      campo: "FechaHistorial",
      claveOrden: "FechaHistorial",
      tipo: "texto",
      alinear: "centro",
      render: (f) => fmt_fecha(f.FechaHistorial),
    },
    {
      titulo: "Línea",
      campo: "Linea",
      claveOrden: "Linea",
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
      titulo: "Dominio",
      campo: "Dominio",
      claveOrden: "Dominio",
      tipo: "texto",
      alinear: "centro",
      render: (f) => <span className={"badge neutro"}>{f.Dominio}</span>,
    },
    {
      titulo: "Patentado",
      campo: "FechaPatentado",
      claveOrden: "FechaPatentado",
      tipo: "texto",
      alinear: "centro",
      render: (f) => fmt_fecha(f.FechaPatentado),
    },
    {
      titulo: "KM",
      campo: "KM",
      claveOrden: "KM",
      tipo: "numeric",
      alinear: "centro",
      render: (f) => (f.KM != null ? fmt_num.format(f.KM) : null),
    },
    {
      titulo: "Asientos",
      campo: "Asientos",
      claveOrden: "Asientos",
      tipo: "numeric",
      alinear: "centro",
    },
    {
      titulo: "Combustible",
      campo: "TipoCombustible",
      claveOrden: "TipoCombustible",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Carrocería",
      campo: "Carroceria",
      claveOrden: "Carroceria",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Código Chasis",
      campo: "ChasisCod",
      claveOrden: "ChasisCod",
      tipo: "texto",
      alinear: "izquierda",
    },
    {
      titulo: "Marca Chasis",
      campo: "ChasisMarca",
      claveOrden: "ChasisMarca",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Modelo Chasis",
      campo: "ChasisModelo",
      claveOrden: "ChasisModelo",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Año Chasis",
      campo: "ChasisAño",
      claveOrden: "ChasisAño",
      tipo: "numeric",
      alinear: "centro",
    },
    {
      titulo: "Código Motor",
      campo: "MotorCod",
      claveOrden: "MotorCod",
      tipo: "texto",
      alinear: "izquierda",
    },
    {
      titulo: "Marca Motor",
      campo: "MotorMarca",
      claveOrden: "MotorMarca",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Modelo Motor",
      campo: "MotorModelo",
      claveOrden: "MotorModelo",
      tipo: "texto",
      alinear: "centro",
    },
  ];

  return (
    <div className="pagina">
      <Filtros config={filtros_parque_movil} onCambio={setFiltros} />
      <div className="contenido">
        <Tabla
          datosTabla={getParqueMovil}
          columnas={columnas_parque_movil}
          filtros={filtros}
          ordenCol="FechaHistorial"
          pkFila="IDParqueMovilHistorial"
          paginacion="cursor"
          seleccionada={seleccionado?.IDParqueMovilHistorial}
          onSeleccionar={setSeleccionado}
          exportar={exportar}
        />
      </div>
    </div>
  );
}
