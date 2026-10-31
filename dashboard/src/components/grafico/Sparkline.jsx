import ReactECharts from "echarts-for-react";

export default function Sparkline({
  datos,
  formato = (v) => new Intl.NumberFormat("es-AR").format(v),
  tipo = "line",
  color = "#3b82f6",
  alto = 90,
}) {
  if (!datos?.length) return null;

  const option = {
    grid: { left: 4, right: 12, top: 0, bottom: 0, containLabel: true },
    yAxis: {
      type: "category",
      show: true,
      data: datos.map((d) => d.x),
      inverse: true,
    },
    xAxis: {
      type: "value",
      show: false,
      min: tipo === "line" ? "dataMin" : 0,
    },
    tooltip: {
      trigger: "axis",
      confine: true,
      extraCssText: "white-space: normal; max-width: 260px;", // la descripción larga baja de línea
      formatter: (p) => {
        const d = datos[p[0].dataIndex];
        return `<b>${d.x}</b>${d.extra ? `<br/>${d.extra}` : ""}<br/>${p[0].marker} ${formato(d.y)}`;
      },
    },
    series: [
      {
        type: tipo,
        barWidth: tipo === "bar" ? "60%" : undefined,
        data: datos.map((d) => d.y),
        smooth: tipo === "line",
        showSymbol: false,
        lineStyle: { width: 2, color },
        itemStyle: { color },
        areaStyle: tipo === "line" ? { color, opacity: 0.12 } : undefined,
      },
    ],
  };
  return (
    <ReactECharts
      option={option}
      notMerge
      opts={{ renderer: "canvas" }}
      style={{ height: alto, width: "100%" }}
    />
  );
}
