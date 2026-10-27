import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import { useMemo } from "react";
import CampoFecha from "../../components/CampoFecha.jsx";

export default function VistaDuracionRepuestos({
  datos,
  desde = "",
  hasta = "",
  onFechas,
}) {
  const option = useMemo(() => {
    const mu = Number(datos.Media);
    const sigma = Number(datos.Desvio);

    if (!sigma) return null;

    const min = Math.max(0, mu - 4 * sigma);
    const max = mu + 4 * sigma;
    const puntos = [];

    for (let i = 0; i <= 100; i++) {
      const x = min + ((max - min) * i) / 100;
      const y =
        Math.exp(-0.5 * ((x - mu) / sigma) ** 2) /
        (sigma * Math.sqrt(2 * Math.PI));
      puntos.push([x, y]);
    }

    return {
      tooltip: { show: false },
      grid: { left: 30, right: 20, top: 30, bottom: 40 },
      xAxis: {
        type: "value",
        name: "Años",
        min,
        max,
        axisLabel: { formatter: (v) => Number(v.toFixed(1)) },
      },
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

  const hayMedia = datos.Media != null;

  return (
    <>
      <div className="kpis">
        <div className="kpi">
          <span className="kpi-titulo">Duración media</span>
          <span className="kpi-valor">
            {hayMedia ? `${fmt_charts.format(Number(datos.Media))} años` : "—"}
          </span>
        </div>

        <CampoFecha
          titulo="Patentado desde"
          valor={desde}
          max={hasta}
          onCommit={(v) => onFechas({ desde: v, hasta })}
        />
        <CampoFecha
          titulo="Patentado hasta"
          valor={hasta}
          min={desde}
          alinear="derecha"
          onCommit={(v) => onFechas({ desde, hasta: v })}
        />
        <div className="kpi">
          <span className="kpi-titulo">Fallas registradas</span>
          <span className="kpi-valor">{String(datos.N)}</span>
        </div>
      </div>

      <div className="grafico-card">
        {option ? (
          <Grafico option={option} alto="100%" />
        ) : (
          <p className="vacio-grafico">Sin datos suficientes para este rango</p>
        )}
      </div>
    </>
  );
}
