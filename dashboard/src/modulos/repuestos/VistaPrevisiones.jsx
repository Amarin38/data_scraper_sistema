import { useMemo } from "react";
import Grafico from "../../components/grafico/Grafico.jsx";
import { fmt_charts } from "../../constants.js";

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

  return <Grafico option={option} alto={320} />;
}
