import { useMemo } from "react";
import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import Kpis from "../../components/grafico/Kpis.jsx";
import CampoFecha from "../../components/CampoFecha.jsx";
import { useTemaOscuro } from "../../hooks/useTemaOscuro.js";

const fmtFecha = (iso) => iso.split("-").reverse().join("/");

export default function VistaPrevisiones({
  datos,
  desde = "",
  hasta = "",
  onFechas,
}) {
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
  const { kpis, consumoKpi, stockKpi } = useMemo(() => {
    const nums = (tipo) =>
      datos
        .filter((d) => d.Tipo === tipo)
        .sort((a, b) => a.Mes.localeCompare(b.Mes))
        .map((d) => Number(d.Cantidad));
    const suma = (a) => a.reduce((s, v) => s + v, 0);

    const consumo = nums("Consumo");
    const prev = nums("Prevision");
    const cob = datos.cobertura;

    const ult12 = consumo.slice(-12);
    const promConsumo = ult12.length ? suma(ult12) / ult12.length : null;

    const horizonte = (n) => {
      const tono = `prev${n}`;
      if (prev.length < n) {
        return {
          titulo: `Próximos ${n} meses`,
          valor: "—",
          detalle: "sin previsión",
          tono,
        };
      }
      const obj = cob?.[`Objetivo${n}`];
      return {
        titulo: `Próximos ${n} meses`,
        valor: fmt_charts.format(suma(prev.slice(0, n))),
        detalle: obj != null ? `Stock objetivo: ${fmt_charts.format(obj)}` : "",
        tono,
      };
    };

    // stock actual + cuándo se agota, en una sola tarjeta
    const stock = cob?.Stock != null ? Number(cob.Stock) : null;
    const alDia = cob?.FechaStock ? `al ${fmtFecha(cob.FechaStock)}` : "";
    const st = {
      valor: stock != null ? fmt_charts.format(stock) : "—",
      extra: null,
      detalle: alDia || "sin dato de stock",
      tono: undefined,
    };

    if (stock != null) {
      if (stock <= 0) {
        st.extra = "sin stock";
        st.tono = "mal";
      } else if (cob.Agotamiento) {
        const meses =
          (new Date(cob.Agotamiento) - new Date()) / (30.44 * 24 * 3600 * 1000);
        if (meses <= 0) {
          st.extra = "ya sin stock";
          st.detalle = `${alDia} · según lo previsto`;
          st.tono = "mal";
        } else {
          st.extra = `se agota ${fmtFecha(cob.Agotamiento)}`;
          st.detalle = `${alDia} · en ≈ ${fmt_charts.format(meses)} meses`;
          st.tono = meses <= 3 ? "mal" : undefined;
        }
      } else if (cob.MesesCubiertos > 0) {
        st.extra = "no se agota";
        st.detalle = `${alDia} · en los ${cob.MesesCubiertos} meses previstos`;
        st.tono = "ok";
      } else {
        st.detalle = `${alDia} · la previsión no llega a esa fecha`;
      }
    }

    return {
      kpis: [horizonte(3), horizonte(6), horizonte(12)],
      consumoKpi: {
        titulo: "Consumo mensual",
        valor: promConsumo != null ? fmt_charts.format(promConsumo) : "—",
        detalle: "promedio últimos 12 meses",
      },
      stockKpi: st,
    };
  }, [datos]);
  return (
    <>
      <Kpis items={kpis} className="kpis-horizontes" />

      <div className="kpis kpis-stock">
        <div className={`kpi${stockKpi.tono ? ` ${stockKpi.tono}` : ""}`}>
          <span className="kpi-titulo">Stock actual</span>
          <span className="kpi-valor">
            {stockKpi.valor}
            {stockKpi.extra && (
              <>
                {" "}
                <span className="kpi-sep">|</span>{" "}
                <span className="kpi-meses">{stockKpi.extra}</span>
              </>
            )}
          </span>
          <span className="kpi-detalle">{stockKpi.detalle}</span>
        </div>

        <div className="kpi">
          <span className="kpi-titulo">{consumoKpi.titulo}</span>
          <span className="kpi-valor">{consumoKpi.valor}</span>
          <span className="kpi-detalle">{consumoKpi.detalle}</span>
        </div>
      </div>

      {onFechas && (
        <div className="kpis kpis-filtros">
          <CampoFecha
            titulo="Consumo desde"
            valor={desde}
            max={hasta}
            onCommit={(v) => onFechas({ desde: v, hasta })}
          />
          <CampoFecha
            titulo="Consumo hasta"
            valor={hasta}
            min={desde}
            alinear="derecha"
            onCommit={(v) => onFechas({ desde, hasta: v })}
          />
        </div>
      )}

      <div className="grafico-card">
        <Grafico option={option} alto="100%" />
      </div>
    </>
  );
}
