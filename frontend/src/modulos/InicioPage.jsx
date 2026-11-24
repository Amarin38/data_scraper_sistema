import { useEffect, useState } from "react";
import TarjetaMicro from "../components/grafico/TarjetaMicro.jsx";
import TarjetaRanking from "../components/grafico/TarjetaRanking.jsx";
import ListaCompacta from "../components/grafico/ListaCompacta.jsx";
import {
  datos_rapidos_ep,
  fmt_spark,
  fmt_dinero,
  fmt_dinero_corto,
} from "../constants.js";
import { getCacheado } from "../api/client.js";
import PanelLateral from "../components/grafico/PanelLateral.jsx";
import { vistas } from "./repuestos/vistasRepuesto.js";

const getDatosRapidos = () => getCacheado(datos_rapidos_ep);

const HORIZONTES = [3, 6, 12];

export default function InicioPage() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const [seleccionado, setSeleccionado] = useState(null);
  const idSel = seleccionado?.IDRepuesto;

  useEffect(() => {
    let cancelado = false;
    getDatosRapidos()
      .then((d) => !cancelado && setDatos(d))
      .catch(
        (e) =>
          !cancelado &&
          setError(e.message ?? "No se pudieron cargar los datos"),
      );
    return () => {
      cancelado = true;
    };
  }, []);

  const cargando = !datos && !error;
  const consumo = datos?.mayor_stock ?? [];
  const gasto = datos?.mayor_gasto ?? [];
  const crit = datos?.crit_sin_exist ?? [];

  const opcionesImportar = HORIZONTES.map((n) => {
    const filas = (n === 3 ? datos?.importar : datos?.[`importar_${n}`]) ?? [];
    return {
      id: n,
      etiqueta: `${n} meses`,
      titulo: `Próximos a importar (previsión ${n} meses)`,
      filas,
      valor: filas.length,
    };
  });

  const opcionesGastoConsumo = [
    {
      id: "gasto",
      etiqueta: "Mayor gasto",
      titulo: "Artículos de mayor gasto (último mes)",
      filas: gasto,
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
      filas: consumo,
      columnas: [
        {
          campo: "Cantidad",
          formatoTitulo: (v) => fmt_spark.format(Number(v)),
        },
      ],
      textoSuma: "Unidades del top 10",
      color: "#f59e0b",
    },
  ];

  return (
    <div className="inicio">
      <header className="inicio-cabecera">
        <h1>Estadísticas rápidas</h1>
        <p>Resumen de estadísticas rápidas del sistema.</p>
      </header>
      <div className="tarjetas">
        <TarjetaRanking
          opciones={opcionesImportar}
          etiquetaSelector="Horizonte de previsión"
          columnas={[
            {
              campo: "Prevision",
              titulo: "Previsto",
              formatoTitulo: (v) => fmt_spark.format(Number(v)),
            },
            {
              campo: "Stock",
              titulo: "Stock",
              formatoTitulo: (v) => fmt_spark.format(Number(v)),
            },
            {
              campo: "Faltante",
              titulo: "Importar",
              destacada: true,
              formatoTitulo: (v) => fmt_spark.format(Number(v)),
              formatoLista: (v) => fmt_spark.format(Math.ceil(Number(v))),
            },
          ]}
          detalle="repuestos con faltante según previsión"
          color="#6366f1"
          cols={3}
          posicion={false}
          onSeleccionar={setSeleccionado}
          seleccionado={idSel}
          cargando={cargando}
          error={error}
        />
        <TarjetaRanking
          opciones={opcionesGastoConsumo}
          etiquetaSelector="Ranking del último mes"
          onSeleccionar={setSeleccionado}
          seleccionado={idSel}
          cargando={cargando}
          error={error}
          posicion={false}
        />
        <TarjetaMicro
          titulo="Críticos sin stock"
          cols={1}
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
            onSeleccionar={setSeleccionado}
            seleccionado={idSel}
            vacioTexto="Ningún crítico sin stock"
          />
        </TarjetaMicro>
      </div>
      <div className={`inicio-drawer${seleccionado ? " con-panel" : ""}`}>
        <PanelLateral
          vistas={vistas}
          subtitulo=""
          seleccionado={seleccionado}
          setSeleccionado={setSeleccionado}
        />
      </div>
    </div>
  );
}
