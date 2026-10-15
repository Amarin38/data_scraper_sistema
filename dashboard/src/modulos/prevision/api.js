import { get } from "../../api/client.js";
import { previsiones_ep, conjuntos_ep } from "../../constants.js";

export const getPrevisiones = (filtros) => get(previsiones_ep, filtros);
export const getConjuntos = () => get(conjuntos_ep);
