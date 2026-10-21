import { useMemo } from "react";
import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import Kpis from "../../components/grafico/Kpis.jsx";

export default function VistaPrevisiones({ datos }) {
  const option = useMemo(() => {
    // pares [mes, valor] por serie
    const par = (d) => [d.Mes, Number(d.Cantidad)];
    const consumo = datos.filter((d) => d.Tipo === "Consumo").map(par);
    const prev = datos.filter((d) => d.Tipo === "Prevision").map(par);
    const ultimo = consumo[consumo.length - 1];
    const prevConectada = ultimo ? [ultimo, ...prev] : prev;

    // todos los meses, sin repetir y en orden ("YYYY-MM" ordena bien como texto)
    const meses = [...new Set(datos.map((d) => d.Mes))].sort();

    return {
      tooltip: { trigger: "axis", valueFormatter: (v) => fmt_charts.format(v) },
      legend: {},
      grid: { left: 50, right: 20, top: 40, bottom: 70 },
      xAxis: { type: "category", data: meses },
      yAxis: { type: "value" },
      markArea: {
        silent: true,
        itemStyle: { color: "rgba(245, 158, 11, 0.07)" },
        data:
          prev.length > 0
            ? [[{ xAxis: prev[0][0] }, { xAxis: prev[prev.length - 1][0] }]]
            : [],
      },
      series: [
        {
          name: "Consumo",
          type: "line",
          smooth: true,
          data: consumo,
          symbolSize: 6,
          itemStyle: { color: "#3b82f6" },
        },
        {
          name: "Previsión",
          type: "line",
          smooth: true,
          data: prevConectada,
          symbolSize: 6,
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2, type: "dashed" },
        },
      ],
    };
  }, [datos]);

  // datos rapidos
  const kpis = useMemo(() => {
    const nums = (tipo) =>
      datos
        .filter((d) => d.Tipo === tipo)
        .sort((a, b) => a.Mes.localeCompare(b.Mes))
        .map((d) => Number(d.Cantidad));
    const suma = (a) => a.reduce((s, v) => s + v, 0);

    const consumo = nums("Consumo").slice(-12);
    const prev = nums("Prevision");
    const promConsumo = consumo.length ? suma(consumo) / consumo.length : null;
    const promPrev = prev.length ? suma(prev) / prev.length : null;
    const variacion =
      promConsumo && promPrev != null
        ? ((promPrev - promConsumo) / promConsumo) * 100
        : null;

    return [
      {
        titulo: "Consumo mensual",
        valor: promConsumo != null ? fmt_charts.format(promConsumo) : "—",
        detalle: "promedio últimos 12 meses",
      },
      {
        titulo: "Prevision mensual",
        valor: promPrev != null ? fmt_charts.format(promPrev) : "—",
        detalle: "promedio próximos meses",
      },
      {
        titulo: "Total previsto",
        valor: fmt_charts.format(suma(prev)),
        detalle: `${prev.length} meses`,
      },
      {
        titulo: "Variación",
        valor:
          variacion != null
            ? `${variacion > 0 ? "+" : ""}${fmt_charts.format(variacion)}%`
            : "—",
        detalle: "previsión vs consumo",
      },
    ];
  }, [datos]);

  return (
    <>
      <Kpis items={kpis} />
      <div className="grafico-card">
        <Grafico option={option} alto="100%" />
      </div>
    </>
  );
}
