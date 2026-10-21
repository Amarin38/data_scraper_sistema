import TablaGrafico from "../../components/grafico/TablaGrafico.jsx";
import { get, getCacheado } from "../../api/client.js";
import {
  repuestos_ep,
  indices_ep,
  previsiones_ep,
  duraciones_ep,
  conjuntos_ep,
} from "../../constants.js";
import VistaIndicesConsumo from "./VistaIndicesConsumo.jsx";
import VistaPrevisiones from "./VistaPrevisiones.jsx";
import VistaDuracionRepuestos from "./VistaDuracionRepuestos.jsx";

const getRepuestos = (filtros) => get(repuestos_ep, filtros);
const getIndice = (id) => get(`${indices_ep}/${id}`);
const getPrevision = (id) => get(`${previsiones_ep}/${id}`);
const getDuracion = (id) =>
  get(`${duraciones_ep}/${id}`).then((d) => (d?.Desvio ? d : null));
const getConjuntos = () => getCacheado(conjuntos_ep);

const vistas = {
  "Índices de Consumo": { get: getIndice, Vista: VistaIndicesConsumo },
  Previsiones: { get: getPrevision, Vista: VistaPrevisiones },
  "Duracion Repuestos": { get: getDuracion, Vista: VistaDuracionRepuestos },
};

const filtros_repuestos = [
  { tipo: "select", campo: "conjunto", opciones: getConjuntos },
  { tipo: "texto", campo: "descripcion", placeholder: "Buscar descripcion..." },
  { tipo: "texto", campo: "codigo", placeholder: "Buscar código..." },
  { tipo: "check", campo: "critico", etiqueta: "Solo críticos" },
];

export default function RepuestosPage() {
  const columnas_repuestos = [
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
      titulo: "Condicion",
      campo: "Condicion",
      claveOrden: "Condicion",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Conjunto",
      campo: "Conjunto",
      claveOrden: "Conjunto",
      tipo: "texto",
      alinear: "centro",
    },
    {
      titulo: "Critico",
      campo: "Critico",
      claveOrden: "Critico",
      tipo: "bool",
      alinear: "centro",
      render: (f) => <input type="checkbox" checked={!!f.Critico} readOnly />,
    },
  ];

  return (
    <TablaGrafico
      datosTabla={getRepuestos}
      vistas={vistas}
      subtitulo="Indice x100 repuestos."
      columnas={columnas_repuestos}
      ordenCol="Descripcion"
      pkFila="IDRepuesto"
      filtrosConfig={filtros_repuestos}
    />
  );
}
