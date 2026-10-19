export const estadisticas_ep = "/estadisticas";
export const repuestos_ep = "/repuestos";

export const indices_ep = `${estadisticas_ep}/indices-consumo`;
export const previsiones_ep = `${estadisticas_ep}/previsiones`;
export const duraciones_ep = `${estadisticas_ep}/duracion-repuestos`;

export const conjuntos_ep = `${repuestos_ep}/conjuntos`;

export const fmt_charts = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 1,
});
