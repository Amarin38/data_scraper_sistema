import { get } from "../../api/client.js";
import { indices_ep, previsiones_ep, duraciones_ep } from "../../constants.js";
import VistaIndicesConsumo from "./VistaIndicesConsumo.jsx";
import VistaPrevisiones from "./VistaPrevisiones.jsx";
import VistaDuracionRepuestos from "./VistaDuracionRepuestos.jsx";

const getIndice = (id) => get(`${indices_ep}/${id}`);
const getPrevision = async (id, { desde, hasta } = {}) => {
  const params = { consumo_desde: desde, consumo_hasta: hasta };
  const [serie, cobertura] = await Promise.all([
    get(`${previsiones_ep}/${id}`, params),
    get(`${previsiones_ep}/${id}/cobertura`, params),
  ]);
  serie.cobertura = cobertura;
  return serie;
};
const getDuracion = (id, { desde, hasta } = {}) =>
  get(`${duraciones_ep}/${id}`, {
    patentado_desde: desde,
    patentado_hasta: hasta,
  });

const pad = (n) => String(n).padStart(2, "0");
const iso = (d) =>
  `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
// día 1 del mes, hace n meses
const haceMeses = (n) => {
  const d = new Date();
  d.setDate(1);
  d.setMonth(d.getMonth() - n);
  return iso(d);
};

export const vistas = {
  "Índices de Consumo": { get: getIndice, Vista: VistaIndicesConsumo },
  Previsiones: {
    get: getPrevision,
    Vista: VistaPrevisiones,
    fechas0: () => ({ desde: haceMeses(24), hasta: "" }),
  },
  "Duracion Repuestos": { get: getDuracion, Vista: VistaDuracionRepuestos },
};
