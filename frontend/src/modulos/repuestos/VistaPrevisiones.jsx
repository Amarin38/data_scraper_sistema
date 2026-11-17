import { useMemo } from "react";
import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import Kpis from "../../components/grafico/Kpis.jsx";
import { useTemaOscuro } from "../../hooks/useTemaOscuro.js";

export default function VistaPrevisiones({ datos }) {
  const oscuro = useTemaOscuro();
  const texto = oscuro ? "#e5e7eb" : "#1f2937";

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
      tooltip: {
        trigger: "axis",
        confine: true,
        valueFormatter: (v) => fmt_charts.format(v),
      },
      legend: {
        top: 6,
        right: 16,
        orient: "horizontal",
        itemGap: 20,
        itemWidth: 22,
        itemHeight: 12,
        textStyle: { color: texto, fontSize: 14, fontWeight: 600 },
        backgroundColor: oscuro ? "#1f2937" : "#fff",
        borderColor: oscuro ? "#374151" : "#e2e8f0",
        borderWidth: 1,
        borderRadius: 10,
        padding: [8, 14],
      },
      grid: { top: 56, left: 50, right: 30, bottom: 36 },
      xAxis: { type: "category", data: meses },
      yAxis: { type: "value" },
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
          markArea: {
            silent: true,
            itemStyle: { color: "rgba(245, 158, 11, 0.07)" },
            data:
              prev.length > 0
                ? [[{ xAxis: prev[0][0] }, { xAxis: prev[prev.length - 1][0] }]]
                : [],
          },
        },
      ],
    };
  }, [datos, oscuro, texto]);

  // datos rapidos
  const kpis = useMemo(() => {
    const nums = (tipo) =>
      datos
        .filter((d) => d.Tipo === tipo)
        .sort((a, b) => a.Mes.localeCompare(b.Mes))
        .map((d) => Number(d.Cantidad));
    const suma = (a) => a.reduce((s, v) => s + v, 0);

    const consumo = nums("Consumo");
    const prev = nums("Prevision");

    const ult12 = consumo.slice(-12);
    const promConsumo = ult12.length ? suma(ult12) / ult12.length : null;

    // total previsto de los próximos n meses, comparado con los n meses previos de consumo
    const horizonte = (n) => {
      if (prev.length < n) {
        return {
          titulo: `Próximos ${n} meses`,
          valor: "—",
          detalle: "sin previsión",
        };
      }
      const total = suma(prev.slice(0, n));
      const real = suma(consumo.slice(-n));
      const variacion =
        consumo.length >= n && real > 0 ? ((total - real) / real) * 100 : null;
      return {
        titulo: `Próximos ${n} meses`,
        valor: fmt_charts.format(total),
        detalle:
          variacion != null
            ? `${variacion > 0 ? "+" : ""}${fmt_charts.format(variacion)}% vs. ${n} meses previos`
            : `${n} meses`,
      };
    };

    return [
      {
        titulo: "Consumo mensual",
        valor: promConsumo != null ? fmt_charts.format(promConsumo) : "—",
        detalle: "promedio últimos 12 meses",
      },
      horizonte(3),
      horizonte(6),
      horizonte(12),
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
