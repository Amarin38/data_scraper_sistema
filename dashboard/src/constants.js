export const inicio_ep = "/inicio";
export const estadisticas_ep = "/estadisticas";
export const repuestos_ep = "/repuestos";
export const ficha_stock_ep = "/ficha-stock";
export const existencia_stock_ep = "/existencia-stock";
export const parque_movil_ep = "/parque-movil";
export const cabeceras_ep = "/cabeceras";

export const indices_ep = `${estadisticas_ep}/indices-consumo`;
export const previsiones_ep = `${estadisticas_ep}/previsiones`;
export const duraciones_ep = `${estadisticas_ep}/duracion-repuestos`;

export const movimientos_ep = `${ficha_stock_ep}/movimientos`;
export const conjuntos_ep = `${repuestos_ep}/conjuntos`;

export const fecha_hoy = () => new Date().toLocaleDateString("en-CA");

export const fmt_charts = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 1,
});

export const fmt_num = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
