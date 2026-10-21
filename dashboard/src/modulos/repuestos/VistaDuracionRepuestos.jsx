import { useMemo } from "react";
import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import Kpis from "../../components/grafico/Kpis.jsx";

export default function VistaDuracionRepuestos({ datos }) {
  const option = useMemo(() => {
    const mu = Number(datos.Media);
    const sigma = Number(datos.Desvio);

    if (!sigma) return null;

    const desde = Math.max(0, mu - 4 * sigma);
    const hasta = mu + 4 * sigma;
    const puntos = [];

    for (let i = 0; i <= 100; i++) {
      const x = desde + ((hasta - desde) * i) / 100;
      const y =
        Math.exp(-0.5 * ((x - mu) / sigma) ** 2) /
        (sigma * Math.sqrt(2 * Math.PI));
      puntos.push([x, y]);
    }

    return {
      tooltip: { show: false },
      grid: { left: 30, right: 20, top: 30, bottom: 40 },
      xAxis: { type: "value", name: "Años", min: desde, max: hasta },
      yAxis: { type: "value", show: false },
      series: [
        {
          type: "line",
          smooth: true,
          showSymbol: false,
          data: puntos,
          itemStyle: { color: "#3b82f6" },
          areaStyle: { color: "rgba(59, 130, 246, 0.15)" },
          markLine: {
            symbol: "none",
            label: { formatter: `Media: ${mu.toFixed(1)} años` },
            lineStyle: { color: "#d64545", type: "dashed" },
            data: [{ xAxis: mu }],
          },
        },
      ],
    };
  }, [datos]);

  const kpis = [
    {
      titulo: "Duración media",
      valor: `${fmt_charts.format(Number(datos.Media))} años`,
    },
    {
      titulo: "Desvío",
      valor: `± ${fmt_charts.format(Number(datos.Desvio))} años`,
    },
    { titulo: "Fallas registradas", valor: String(datos.N) },
  ];

  return (
    <>
      <Kpis items={kpis} />
      <div className="grafico-card">
        <Grafico option={option} alto="100%" />
      </div>
    </>
  );
}
