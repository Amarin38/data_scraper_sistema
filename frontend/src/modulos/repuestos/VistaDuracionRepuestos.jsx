import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import { useMemo } from "react";
import CampoFecha from "../../components/CampoFecha.jsx";

const UMBRAL_DISCONTINUADO_ANIOS = 2;

const discontinuado = (f) =>
  f &&
  new Date(f) <
    new Date(Date.now() - UMBRAL_DISCONTINUADO_ANIOS * 365 * 24 * 3600 * 1000);

// "2,9 años | 34,8 meses"
const aniosYMeses = (a) =>
  a == null
    ? null
    : [
        `${fmt_charts.format(Number(a))} años`,
        `${fmt_charts.format(Number(a) * 12)} meses`,
      ];

export default function VistaDuracionRepuestos({
  datos,
  desde = "",
  hasta = "",
  onFechas,
}) {
  const option = useMemo(() => {
    const curva = datos.Curva ?? [];
    if (curva.length < 2) return null;
    const med = datos.Mediana != null ? Number(datos.Mediana) : null;

    return {
      tooltip: {
        trigger: "axis",
        formatter: ([p]) =>
          `${p.value[0].toFixed(1)} años: ${Math.round(p.value[1] * 100)} % sigue en uso`,
      },
      grid: { left: 45, right: 20, top: 30, bottom: 40 },
      xAxis: {
        type: "value",
        name: "Años",
        min: 0,
        axisLabel: { formatter: (v) => Number(v.toFixed(1)) },
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 1,
        axisLabel: { formatter: (v) => `${Math.round(v * 100)}%` },
      },
      series: [
        {
          type: "line",
          step: "end",
          showSymbol: false,
          data: curva,
          itemStyle: { color: "#3b82f6" },
          areaStyle: { color: "rgba(59, 130, 246, 0.15)" },
          markLine:
            med == null
              ? undefined
              : {
                  symbol: "none",
                  label: { formatter: `Mediana: ${med.toFixed(1)} años` },
                  lineStyle: { color: "#d64545", type: "dashed" },
                  data: [{ xAxis: med }],
                },
        },
      ],
    };
  }, [datos]);

  const hayMedia = datos.Media != null;
  const disc = discontinuado(datos.UltimoCambio);
  const sinMediana = datos.Mediana == null && datos.P25 != null;

  return (
    <>
      <div className="kpis kpis-datos">
        <div className="kpi">
          <span className="kpi-titulo">
            {sinMediana ? "Se cambia el 25 % a los" : "Duración"}
          </span>
          <span className="kpi-valor">
            {(() => {
              const v = aniosYMeses(datos.Mediana ?? datos.P25);
              return v ? (
                <>
                  {v[0]} <span className="kpi-sep">|</span>{" "}
                  <span className="kpi-meses">{v[1]}</span>
                </>
              ) : (
                "—"
              );
            })()}
          </span>
          <span className="kpi-detalle">
            {sinMediana
              ? "Menos de la mitad se cambia: no hay duración típica"
              : datos.Mediana == null
                ? datos.Curva?.length
                  ? "Menos de un cuarto se cambia"
                  : ""
                : disc
                  ? "Ya no se usa: refleja el período en que se usó"
                  : datos.N < 30
                    ? "Pocos datos: poco confiable"
                    : "El 50 % dura más que esto"}
          </span>
        </div>

        <div className="kpi">
          <span className="kpi-titulo">Cambios</span>
          <span className="kpi-valor">{String(datos.N)}</span>
          <span className="kpi-detalle">cambios registrados</span>
        </div>

        <div className={`kpi ${disc ? "disc" : ""}`}>
          <span className="kpi-titulo">Último cambio</span>
          <span className="kpi-valor">
            {datos.UltimoCambio ? datos.UltimoCambio.slice(0, 4) : "—"}
          </span>
          <span className="kpi-detalle">
            {datos.UltimoCambio
              ? datos.UltimoCambio.split("-").reverse().join("/")
              : ""}
          </span>
        </div>
      </div>

      <div className="kpis kpis-filtros">
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
