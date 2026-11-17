import { useEffect, useMemo, useState } from "react";
import { fmt_charts } from "../../constants.js";
import Grafico from "../../components/grafico/Grafico.jsx";
import Kpis from "../../components/grafico/Kpis.jsx";
import { useTemaOscuro } from "../../hooks/useTemaOscuro.js";

const ROJO = "#d64545";
const VERDE = "#2e9e5b";
const GRIS = "#999";
const UMBRAL_ROJO = 1.3;
const UMBRAL_VERDE = 0.8;

const coma = (n, dec = 2) => Number(n).toFixed(dec).replace(".", ",");
const color = (rel) =>
  rel > UMBRAL_ROJO ? ROJO : rel < UMBRAL_VERDE ? VERDE : GRIS;

// achica la letra según el largo del nombre para que no se corte en la tarjeta
const ajustar = (txt) => {
  const t = String(txt);
  const tam = t.length > 12 ? "0.6em" : t.length > 9 ? "0.75em" : "1em";
  return <span style={{ fontSize: tam, whiteSpace: "nowrap" }}>{t}</span>;
};

export default function VistaIndicesConsumo({ datos }) {
  const oscuro = useTemaOscuro();

  const option = useMemo(() => {
    const texto = oscuro ? "#e5e7eb" : "#1f2937";
    const tenue = oscuro ? "#9ca3af" : "#6b7280";
    const eje = oscuro ? "#4b5563" : "#9ca3af";

    const orden = [...datos].sort(
      (a, b) => Number(b.Indice) - Number(a.Indice),
    );

    return {
      tooltip: { show: false },
      grid: { left: 120, right: 140, top: 8, bottom: 8 },
      xAxis: { type: "value", show: false },
      yAxis: {
        type: "category",
        inverse: true,
        data: orden.map((d) => d.Deposito),
        axisLabel: { color: texto, fontSize: 13 },
        axisLine: { lineStyle: { color: eje } },
        axisTick: { show: false },
      },
      series: [
        {
          type: "bar",
          barMaxWidth: 24,
          data: orden.map((d) => {
            const rel = Number(d.IndiceRelativo);
            const valor = Number(d.Indice) * 100;
            const c = color(rel);
            return {
              value: +valor.toFixed(1),
              itemStyle: { color: c, borderRadius: [0, 3, 3, 0] },
              label: {
                show: true,
                position: "right",
                formatter: `{v|${fmt_charts.format(valor)}}  {r|×${coma(rel)}}`,
                rich: {
                  v: { color: texto, fontWeight: 700, fontSize: 13 },
                  r: {
                    color: c === GRIS ? tenue : c,
                    fontWeight: 600,
                    fontSize: 12,
                  },
                },
              },
            };
          }),
        },
      ],
    };
  }, [datos, oscuro]);

  const kpis = useMemo(() => {
    const rel = (d) => Number(d.IndiceRelativo);
    const global = Number(datos[0]?.IndiceGlobal) * 100;
    const peor = [...datos].sort((a, b) => rel(b) - rel(a))[0];
    const mejor = [...datos]
      .filter((d) => rel(d) > 0)
      .sort((a, b) => rel(a) - rel(b))[0];
    const rojas = datos.filter((d) => rel(d) > UMBRAL_ROJO).length;

    return [
      {
        titulo: "Índice global",
        valor: fmt_charts.format(global),
        detalle: "x100 · referencia (×1,00)",
      },
      {
        titulo: "Peor cabecera",
        valor: peor?.Deposito ?? "—",
        detalle: peor ? `×${coma(rel(peor))} el índice global` : null,
        tono: peor && rel(peor) > UMBRAL_ROJO ? "mal" : undefined,
      },
      {
        titulo: "Mejor cabecera",
        valor: mejor?.Deposito ?? "—",
        detalle: mejor ? `×${coma(rel(mejor))} el índice global` : null,
        tono: mejor && rel(mejor) < UMBRAL_VERDE ? "ok" : undefined,
      },
      {
        titulo: "Cabeceras en rojo",
        valor: `${rojas} de ${datos.length}`,
        tono: rojas > 0 ? "mal" : "ok",
        detalle: `relativo > ${coma(UMBRAL_ROJO, 1)}`,
      },
    ];
  }, [datos]);

  return (
    <div className="indices-vista">
      <Kpis items={kpis} className="indices" />
      <div className="grafico-card indices-grafico">
        <Grafico option={option} alto="100%" />
        <div className="indices-leyenda">
          <span>
            <i style={{ background: ROJO }} /> relativo &gt; 1,3
          </span>
          <span>
            <i style={{ background: GRIS }} /> 0,8 a 1,3
          </span>
          <span>
            <i style={{ background: VERDE }} /> relativo &lt; 0,8
          </span>
        </div>
      </div>
    </div>
  );
}
