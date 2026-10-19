import TablaGrafico from "../../components/grafico/TablaGrafico.jsx";
import { get } from "../../api/client.js";
import {
  repuestos_ep,
  indices_ep,
  previsiones_ep,
  duraciones_ep,
} from "../../constants.js";
import VistaIndicesConsumo from "./VistaIndicesConsumo.jsx";
import VistaPrevisiones from "./VistaPrevisiones.jsx";
import VistaDuracionRepuestos from "./VistaDuracionRepuestos.jsx";

export default function RepuestosPage() {
  const getRepuestos = (filtros) => get(repuestos_ep, filtros);
  const getIndice = (id) => get(`${indices_ep}/${id}`);
  const getPrevision = (id) => get(`${previsiones_ep}/${id}`);
  const getDuracion = (id) => get(`${duraciones_ep}/${id}`);

  const vistas = {
    "Índices de Consumo": { get: getIndice, Vista: VistaIndicesConsumo },
    Previsiones: { get: getPrevision, Vista: VistaPrevisiones },
    "Duracion Repuestos": { get: getDuracion, Vista: VistaDuracionRepuestos },
  };

  const columnas_repuestos = [
    {
      titulo: "Codigo",
      campo: "Codigo",
      claveOrden: "Codigo",
      alinear: "centro",
    },
    {
      titulo: "Repuesto",
      campo: "Descripcion",
      claveOrden: "Descripcion",
      alinear: "izquierda",
    },
    {
      titulo: "Condicion",
      campo: "Condicion",
      claveOrden: "Condicion",
      alinear: "centro",
    },
    {
      titulo: "Conjunto",
      campo: "Conjunto",
      claveOrden: "Conjunto",
      alinear: "centro",
    },
    {
      titulo: "Critico",
      campo: "Critico",
      claveOrden: "Critico",
      alinear: "centro",
      render: (f) => <input type="checkbox" checked={!!f.Critico} readOnly />,
    },
  ];

  return (
    <TablaGrafico
      datosTabla={getRepuestos}
      vistas={vistas}
      subtitulo={"Indice x100 repuestos."}
      columnas={columnas_repuestos}
      ordenCol="Descripcion"
      pkFila="IDRepuesto"
    />
  );
}
