import { useMemo } from "react";
import Grafico from "../../components/grafico/Grafico.jsx";
import { get } from "../../api/client.js";

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

  return (
    <Grafico option={option} alto={Math.max(300, datos.length * 28 + 60)} />
  );
}
