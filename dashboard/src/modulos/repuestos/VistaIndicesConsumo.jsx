import { useMemo } from "react";
import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import Kpis from "../../components/grafico/Kpis.jsx";

export default function VistaIndicesConsumo({ datos }) {
  const option = useMemo(() => {
    const orden = [...datos].sort(
      (a, b) => Number(b.Indice) - Number(a.Indice),
    );
    return {
      tooltip: {
        formatter: (p) => {
          const d = orden[p.dataIndex];
          return `${d.Deposito}<br/>Índice x100: ${p.value}<br/>Relativo: ${Number(d.IndiceRelativo).toFixed(2)}`;
        },
      },
      grid: { left: 110, right: 40, top: 10, bottom: 30 },
      xAxis: { type: "value" },
      yAxis: {
        type: "category",
        inverse: true,
        data: orden.map((d) => d.Deposito),
      },
      series: [
        {
          type: "bar",
          data: orden.map((d) => {
            const rel = Number(d.IndiceRelativo);
            return {
              value: +(Number(d.Indice) * 100).toFixed(1),
              itemStyle: {
                color: rel > 1.3 ? "#d64545" : rel < 0.8 ? "#2e9e5b" : "#999",
              },
            };
          }),
        },
      ],
    };
  }, [datos]);

  const kpis = useMemo(() => {
    const rel = (d) => Number(d.IndiceRelativo);
    const peor = [...datos].sort((a, b) => rel(b) - rel(a))[0];
    const rojas = datos.filter((d) => rel(d) > 1.3).length;
    return [
      {
        titulo: "Índice global",
        valor: fmt_charts.format(Number(datos[0]?.IndiceGlobal) * 100),
        detalle: "x100",
      },
      {
        titulo: "Peor cabecera",
        valor: peor?.Deposito ?? "—",
        detalle: peor ? `relativo ${rel(peor).toFixed(2)}` : null,
      },
      {
        titulo: "Cabeceras en rojo",
        valor: `${rojas} de ${datos.length}`,
        tono: rojas > 0 ? "mal" : "ok",
        detalle: "relativo > 1,3",
      },
    ];
  }, [datos]);

  return (
    <>
      <Kpis items={kpis} />
      <div
        className="grafico-card"
        style={{ minHeight: datos.length * 28 + 60 }}
      >
        <Grafico option={option} alto="100%" />
      </div>
    </>
  );
}
