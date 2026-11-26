import TarjetaMicro from "../components/grafico/TarjetaMicro.jsx";
import TarjetaRanking from "../components/grafico/TarjetaRanking.jsx";
import ListaCompacta from "../components/grafico/ListaCompacta.jsx";
import PanelFijados from "../components/grafico/PanelFijados.jsx";
import { fmt_spark, fmt_dinero, fmt_dinero_corto } from "../constants.js";

/*
 * Catálogo de paneles de Inicio. Para sumar uno nuevo: agregar una entrada acá.
 *  - fuente: "rapidos" si usa /datos_rapidos (se pide una sola vez si hay al menos uno visible);
 *            null si el panel trae sus propios datos (solo se piden si está visible, porque solo se monta entonces).
 *  - Componente recibe { datos, cargando, error, onSeleccionar, seleccionado }.
 *  - vista: datos de la miniatura que se muestra al agregar (ver components/grafico/Miniatura.jsx).
 */

const HORIZONTES = [3, 6, 12];
const num = (v) => fmt_spark.format(Number(v));

function PanelImportar({
  datos,
  cargando,
  error,
  onSeleccionar,
  seleccionado,
}) {
  const opciones = HORIZONTES.map((n) => {
    const filas = (n === 3 ? datos?.importar : datos?.[`importar_${n}`]) ?? [];
    return {
      id: n,
      etiqueta: `${n} meses`,
      titulo: `Próximos a importar (previsión ${n} meses)`,
      filas,
      valor: filas.length,
    };
  });
  return (
    <TarjetaRanking
      opciones={opciones}
      etiquetaSelector="Horizonte de previsión"
      columnas={[
        { campo: "Prevision", titulo: "Previsto", formatoTitulo: num },
        { campo: "Stock", titulo: "Stock", formatoTitulo: num },
        {
          campo: "Faltante",
          titulo: "Importar",
          destacada: true,
          formatoTitulo: num,
          formatoLista: (v) => fmt_spark.format(Math.ceil(Number(v))),
        },
      ]}
      detalle="repuestos con faltante según previsión"
      color="#6366f1"
      posicion={false}
      onSeleccionar={onSeleccionar}
      seleccionado={seleccionado}
      cargando={cargando}
      error={error}
    />
  );
}

function PanelGasto({ datos, cargando, error, onSeleccionar, seleccionado }) {
  const opciones = [
    {
      id: "gasto",
      etiqueta: "Mayor gasto",
      titulo: "Artículos de mayor gasto (último mes)",
      filas: datos?.mayor_gasto ?? [],
      columnas: [
        {
          campo: "Gasto",
          formatoTitulo: (v) => fmt_dinero_corto.format(Number(v)),
          formatoLista: (v) => fmt_dinero.format(Number(v)),
        },
      ],
      textoSuma: "Suma del top 10",
      color: "#F54927",
    },
    {
      id: "consumo",
      etiqueta: "Mayor consumo",
      titulo: "Artículos de mayor consumo (último mes)",
      filas: datos?.mayor_stock ?? [],
      columnas: [{ campo: "Cantidad", formatoTitulo: num }],
      textoSuma: "Unidades del top 10",
      color: "#f59e0b",
    },
  ];
  return (
    <TarjetaRanking
      opciones={opciones}
      etiquetaSelector="Ranking del último mes"
      onSeleccionar={onSeleccionar}
      seleccionado={seleccionado}
      cargando={cargando}
      error={error}
      posicion={false}
    />
  );
}

function PanelCriticos({
  datos,
  cargando,
  error,
  onSeleccionar,
  seleccionado,
}) {
  const crit = datos?.crit_sin_exist ?? [];
  return (
    <TarjetaMicro
      titulo="Críticos sin stock"
      acento="#dc2626"
      valor={crit.length}
      detalle="repuestos críticos con existencia 0"
      tono={crit.length > 0 ? "mal" : "ok"}
      cargando={cargando}
      error={error}
    >
      <ListaCompacta
        filas={crit}
        max={5}
        onSeleccionar={onSeleccionar}
        seleccionado={seleccionado}
        vacioTexto="Ningún crítico sin stock"
      />
    </TarjetaMicro>
  );
}

function PanelFijadosInicio({ onSeleccionar, seleccionado }) {
  return (
    <PanelFijados onSeleccionar={onSeleccionar} seleccionado={seleccionado} />
  );
}

export const PANELES = [
  {
    id: "fijados",
    titulo: "Repuestos fijados",
    descripcion: "Consumo y gasto de los repuestos que elegís",
    fuente: null,
    Componente: PanelFijadosInicio,
    vista: {
      titulo: "Repuestos fijados",
      valor: "$ 166 M",
      color: "#15803d",
      pildoras: 3,
      filas: [100, 62, 30, 6],
    },
  },
  {
    id: "importar",
    titulo: "Próximos a importar",
    descripcion: "Faltantes según la previsión a 3, 6 y 12 meses",
    fuente: "rapidos",
    Componente: PanelImportar,
    vista: {
      titulo: "Próximos a importar",
      valor: "14",
      color: "#6366f1",
      pildoras: 3,
      filas: [100, 66, 40, 22, 10],
    },
  },
  {
    id: "criticos",
    titulo: "Críticos sin stock",
    descripcion: "Repuestos críticos con existencia 0",
    fuente: "rapidos",
    Componente: PanelCriticos,
    vista: {
      titulo: "Críticos sin stock",
      valor: "1",
      color: "#dc2626",
      filas: [0, 0],
      sinBarra: true,
    },
  },
  {
    id: "gasto",
    titulo: "Mayor gasto y consumo",
    descripcion: "Top 10 del último mes",
    fuente: "rapidos",
    Componente: PanelGasto,
    vista: {
      titulo: "Artículos de mayor gasto",
      valor: "$1354 M",
      color: "#F54927",
      pildoras: 2,
      filas: [100, 55, 42, 25, 14],
    },
  },
];

export const PANELES_POR_ID = Object.fromEntries(PANELES.map((p) => [p.id, p]));
export const POR_DEFECTO = PANELES.map((p) => p.id);
