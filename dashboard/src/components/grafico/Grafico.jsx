import ReactECharts from "echarts-for-react";

const animacionRapida = {
  animationDuration: 300,
  animationEasing: "cubicOut",
  animationDurationUpdate: 150,
  animationEasingUpdate: "cubicOut",
};

export default function Grafico({ option }) {
  return (
    <ReactECharts
      option={{ ...animacionRapida, ...option }}
      notMerge={true}
      style={{ height: 600, width: "100%" }}
    />
  );
}
