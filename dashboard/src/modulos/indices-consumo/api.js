import { get } from "../../api/client.js";
import { indices_ep, conjuntos_ep } from "../../constants.js";

export const getIndicesConsumo = (filtros) => get(indices_ep, filtros);
export const getConjuntos = () => get(conjuntos_ep);
export const getDetalleIndice = (id_repuesto) =>
  get(`${indices_ep}/${id_repuesto}`);
