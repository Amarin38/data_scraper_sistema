import ReactEChartsCore from "echarts-for-react/lib/core";
import * as echarts from "echarts/core";
import { BarChart, LineChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
  MarkAreaComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  BarChart,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkAreaComponent,
  CanvasRenderer,
  MarkLineComponent,
]);

const ReactECharts = ReactEChartsCore.default ?? ReactEChartsCore;

const animacionRapida = {
  animationDuration: 300,
  animationEasing: "cubicOut",
  animationDurationUpdate: 150,
  animationEasingUpdate: "cubicOut",
};

export default function Grafico({ option, alto }) {
  return (
    <ReactECharts
      echarts={echarts}
      option={{ ...animacionRapida, ...option }}
      notMerge={true}
      style={{ height: alto, width: "100%" }}
    />
  );
}
