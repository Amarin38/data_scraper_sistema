import TablaGrafico from "../../components/grafico/TablaGrafico.jsx";
import { vistas } from "./vistasRepuesto.js";
import { get, getCacheado } from "../../api/client.js";
import {
  existencia_stock_ep,
  existencia_stock_exportar_ep,
  conjuntos_ep,
  fmt_cant,
  fmt_fecha,
} from "../../constants.js";

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
const getConjuntos = () => getCacheado(conjuntos_ep);


const exportar = { ruta: existencia_stock_exportar_ep, nombre: "repuestos" };


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
    tipo: "opciones",
    campo: "meses_demanda",
    grupo: "minmax",
    etiqueta: "Demanda de los últimos",
    porDefecto: () => "12",
    lista: [
      ["3", "3 meses"],
      ["6", "6 meses"],
      ["12", "12 meses"],
    ],
  },
  {
    tipo: "numero",
    campo: "meses_min",
    grupo: "minmax",
    etiqueta: "Mínimo (meses)",
    porDefecto: () => "1",
    max: 64,
    menorOIgualQue: "meses_max",
  },
  {
    tipo: "numero",
    campo: "meses_max",
    grupo: "minmax",
    etiqueta: "Máximo (meses)",
    porDefecto: () => "2",
    max: 64,
    mayorOIgualQue: "meses_min",
  },

  { tipo: "check", campo: "critico", etiqueta: "Solo críticos" },
  {
    tipo: "check",
    campo: "solo_con_minmax",
    grupo: "minmax",
    etiqueta: "Solo con mínimo y máximo",
  },
  {
    tipo: "check",
    campo: "incluir_sin_uso",
    etiqueta: "Incluir los que no se usan",
  },
];

const celda = (v) => (v == null ? null : fmt_cant.format(v));

const columnas_repuestos = [
  {
    titulo: "Código",
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
    titulo: "Condición",
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
    ocultarConPanel: true,
    claveOrden: "Conjunto",
    tipo: "texto",
    alinear: "centro",
  },
  {
    titulo: "Crítico",
    campo: "Critico",
    claveOrden: "Critico",
    ocultarConPanel: true,
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
    render: (f) => {
      if (f.SinUso)
        return (
          <span
            className="sin-uso"
            title={`Sin consumo hace más de 2 años · stock ${fmt_cant.format(f.Stock)}`}
          >
            NO SE USA
          </span>
        );
      const stock = Number(f.Stock);
      const clase =
        stock < 0 || Number(f.Reponer) > 0 ? "neg" : stock === 0 ? "cero" : "";
      return (
        <span
          className={clase}
          title={
            f.FechaExistencia
              ? `al ${fmt_fecha(f.FechaExistencia)}`
              : "sin existencia registrada"
          }
        >
          {fmt_cant.format(stock)}
        </span>
      );
    },
  },
  {
    titulo: "Mínimo",
    campo: "Minimo",
    claveOrden: "Minimo",
    ocultarConPanel: true,
    tipo: "numeric",
    alinear: "centro",
    render: (f) => celda(f.Minimo),
  },
  {
    titulo: "Máximo",
    campo: "Maximo",
    claveOrden: "Maximo",
    ocultarConPanel: true,
    tipo: "numeric",
    alinear: "centro",
    render: (f) => celda(f.Maximo),
  },
  {
    titulo: "Reponer",
    campo: "Reponer",
    claveOrden: "Reponer",
    ocultarConPanel: true,
    tipo: "numeric",
    alinear: "centro",
    render: (f) =>
      Number(f.Reponer) > 0 ? (
        <span className="neg">{fmt_cant.format(f.Reponer)}</span>
      ) : null,
  },
];

export default function RepuestosPage() {
  return (
    <TablaGrafico
      datosTabla={getRepuestos}
      vistas={vistas}
      subtitulo=""
      columnas={columnas_repuestos}
      ordenCol="Conjunto"
      ordenDir="asc"
      pkFila="IDRepuesto"
      claseFila={(f) => (Number(f.Reponer) > 0 ? "alerta" : "")}
      filtrosConfig={filtros_repuestos}
      exportar={exportar}
      ordenServidor
    />
  );
}
