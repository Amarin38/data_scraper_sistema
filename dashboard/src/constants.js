export const cabeceras_ep = "/cabeceras";

export const inicio_ep = "/inicio";
export const datos_rapidos_ep = `${inicio_ep}/datos-rapidos`;

export const existencia_stock_ep = "/existencia-stock";
export const existencia_stock_exportar_ep = `${existencia_stock_ep}/exportar`;

export const estadisticas_ep = "/estadisticas";
export const indices_ep = `${estadisticas_ep}/indices-consumo`;
export const previsiones_ep = `${estadisticas_ep}/previsiones`;
export const duraciones_ep = `${estadisticas_ep}/duracion-repuestos`;

export const ficha_stock_ep = "/ficha-stock";
export const movimientos_ep = `${ficha_stock_ep}/movimientos`;
export const ficha_stock_exportar_ep = `${ficha_stock_ep}/exportar`;

export const repuestos_ep = "/repuestos";
export const conjuntos_ep = `${repuestos_ep}/conjuntos`;
export const repuestos_exportar_ep = `${repuestos_ep}/exportar`;

export const parque_movil_ep = "/parque-movil";
export const parque_movil_exportar_ep = `${parque_movil_ep}/exportar`;
export const parque_movil_hist_ep = `${parque_movil_ep}/historiales`;
export const carrocerias_ep = `${parque_movil_ep}/carrocerias`;
export const chasis_marcas_ep = `${parque_movil_ep}/chasis-marcas`;
export const chasis_modelos_ep = `${parque_movil_ep}/chasis-modelos`;
export const motor_marcas_ep = `${parque_movil_ep}/motor-marcas`;
export const motor_modelos_ep = `${parque_movil_ep}/motor-modelos`;

export const fecha_hoy = () => new Date().toLocaleDateString("en-CA");

export const fmt_spark = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 0,
});

export const fmt_charts = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 1,
});

export const fmt_num = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

export const fmt_fecha = (s) => {
  if (!s) return null;
  const [a, m, d] = String(s).slice(0, 10).split("-");
  return `${d}/${m}/${a}`; // 21/10/2026
};
