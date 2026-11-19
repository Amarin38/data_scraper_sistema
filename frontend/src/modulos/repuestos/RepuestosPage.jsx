import TablaGrafico from "../../components/grafico/TablaGrafico.jsx";
import { get, getCacheado } from "../../api/client.js";
import {
  existencia_stock_ep,
  existencia_stock_exportar_ep,
  indices_ep,
  previsiones_ep,
  duraciones_ep,
  conjuntos_ep,
  fmt_num,
  fmt_fecha,
} from "../../constants.js";
import VistaIndicesConsumo from "./VistaIndicesConsumo.jsx";
import VistaPrevisiones from "./VistaPrevisiones.jsx";
import VistaDuracionRepuestos from "./VistaDuracionRepuestos.jsx";

const mesesAFecha = (n) => {
  const d = new Date();
  d.setDate(1);
  d.setMonth(d.getMonth() - Number(n));
  const mes = String(d.getMonth() + 1).padStart(2, "0");
  return `${d.getFullYear()}-${mes}-01`;
};

const getRepuestos = ({ meses_demanda, ...filtros }) =>
  get(existencia_stock_ep, {
    ...filtros,
    demanda_desde: meses_demanda ? mesesAFecha(meses_demanda) : "",
  });
const getIndice = (id) => get(`${indices_ep}/${id}`);
const getPrevision = async (id, { desde, hasta } = {}) => {
  const params = { consumo_desde: desde, consumo_hasta: hasta };
  const [serie, cobertura] = await Promise.all([
    get(`${previsiones_ep}/${id}`, params),
    get(`${previsiones_ep}/${id}/cobertura`, params),
  ]);
  serie.cobertura = cobertura;
  return serie;
};
const getDuracion = (id, { desde, hasta } = {}) =>
  get(`${duraciones_ep}/${id}`, {
    patentado_desde: desde,
    patentado_hasta: hasta,
  });
const getConjuntos = () => getCacheado(conjuntos_ep);

const pad = (n) => String(n).padStart(2, "0");
const iso = (d) =>
  `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
// día 1 del mes, hace n meses
const haceMeses = (n) => {
  const d = new Date();
  d.setDate(1);
  d.setMonth(d.getMonth() - n);
  return iso(d);
};

const exportar = { ruta: existencia_stock_exportar_ep, nombre: "repuestos" };

const vistas = {
  "Índices de Consumo": { get: getIndice, Vista: VistaIndicesConsumo },
  Previsiones: {
    get: getPrevision,
    Vista: VistaPrevisiones,
    fechas0: () => ({ desde: haceMeses(24), hasta: "" }),
  },
  "Duracion Repuestos": { get: getDuracion, Vista: VistaDuracionRepuestos },
};

const filtros_repuestos = [
  {
    tipo: "texto",
    campo: "descripcion",
    etiqueta: "Descripción",
    placeholder: "Buscar...",
  },
  {
    tipo: "texto",
    campo: "codigo",
    etiqueta: "Código",
    placeholder: "Buscar...",
  },
  {
    tipo: "select",
    campo: "conjunto",
    etiqueta: "Conjunto",
    placeholder: "Todos",
    opciones: getConjuntos,
  },
  {
    tipo: "numero",
    campo: "meses_min",
    etiqueta: "Mínimo (meses)",
    porDefecto: () => "1",
    max: 64,
    menorOIgualQue: "meses_max",
  },
  {
    tipo: "numero",
    campo: "meses_max",
    etiqueta: "Máximo (meses)",
    porDefecto: () => "2",
    max: 64,
    mayorOIgualQue: "meses_min",
  },
  {
    tipo: "opciones",
    campo: "meses_demanda",
    etiqueta: "Demanda de los últimos",
    porDefecto: () => "12",
    lista: [
      ["3", "3 meses"],
      ["6", "6 meses"],
      ["12", "12 meses"],
    ],
  },
  { tipo: "check", campo: "critico", etiqueta: "Solo críticos" },
  {
    tipo: "check",
    campo: "solo_con_minmax",
    etiqueta: "Solo con mínimo y máximo",
  },
];

const celda = (v) => (v == null ? "—" : fmt_num.format(v));

const columnas_repuestos = [
  {
    titulo: "Codigo",
    campo: "Codigo",
    claveOrden: "Codigo",
    tipo: "texto",
    alinear: "centro",
  },
  {
    titulo: "Repuesto",
    campo: "Descripcion",
    claveOrden: "Descripcion",
    tipo: "texto",
    alinear: "izquierda",
  },
  {
    titulo: "Condicion",
    campo: "Condicion",
    claveOrden: "Condicion",
    tipo: "texto",
    alinear: "centro",
    render: (f) => (
      <span className={`badge ${f.Condicion === "NUEVO" ? "ok" : "aviso"}`}>
        {f.Condicion}
      </span>
    ),
  },
  {
    titulo: "Conjunto",
    campo: "Conjunto",
    claveOrden: "Conjunto",
    tipo: "texto",
    alinear: "centro",
  },
  {
    titulo: "Critico",
    campo: "Critico",
    claveOrden: "Critico",
    tipo: "bool",
    alinear: "centro",
    render: (f) =>
      f.Critico ? <span className="badge mal">Crítico</span> : null,
  },
  {
    titulo: "Stock",
    campo: "Stock",
    claveOrden: "Stock",
    tipo: "numeric",
    alinear: "centro",
    render: (f) => (
      <span
        className={Number(f.Stock) <= 0 ? "neg" : "pos"}
        title={
          f.FechaExistencia
            ? `al ${fmt_fecha(f.FechaExistencia)}`
            : "sin existencia registrada"
        }
      >
        {fmt_num.format(f.Stock)}
      </span>
    ),
  },
  {
    titulo: "Mínimo",
    campo: "Minimo",
    claveOrden: "Minimo",
    tipo: "numeric",
    alinear: "centro",
    render: (f) => celda(f.Minimo),
  },
  {
    titulo: "Máximo",
    campo: "Maximo",
    claveOrden: "Maximo",
    tipo: "numeric",
    alinear: "centro",
    render: (f) => celda(f.Maximo),
  },
  {
    titulo: "Reponer",
    campo: "Reponer",
    claveOrden: "Reponer",
    tipo: "numeric",
    alinear: "centro",
    render: (f) =>
      f.Reponer == null ? (
        "—"
      ) : (
        <span className={Number(f.Reponer) > 0 ? "neg" : ""}>
          {fmt_num.format(f.Reponer)}
        </span>
      ),
  },
];

export default function RepuestosPage() {
  return (
    <TablaGrafico
      datosTabla={getRepuestos}
      vistas={vistas}
      subtitulo=""
      columnas={columnas_repuestos}
      ordenCol="Descripcion"
      pkFila="IDRepuesto"
      claseFila={(f) => (Number(f.Reponer) > 0 ? "alerta" : "")}
      filtrosConfig={filtros_repuestos}
      exportar={exportar}
      ordenServidor
    />
  );
}
