import { useEffect, useState } from "react";
import TarjetaMicro from "../components/grafico/TarjetaMicro.jsx";
import TarjetaRanking from "../components/grafico/TarjetaRanking.jsx";
import {
  datos_rapidos_ep,
  fmt_spark,
  fmt_dinero,
  fmt_dinero_corto,
} from "../constants.js";
import { getCacheado } from "../api/client.js";

const getDatosRapidos = () => getCacheado(datos_rapidos_ep);

export default function InicioPage() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);

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
  const imp = datos?.importar ?? [];

  return (
    <div className="inicio">
      <header className="inicio-cabecera">
        <h1>Estadísticas rápidas</h1>
        <p>Resumen de estadísticas rápidas del sistema.</p>
      </header>
      <div className="tarjetas">
        <TarjetaRanking
          titulo="Próximos a importar (previsión 3 meses)"
          filas={imp}
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
          valor={imp.length}
          detalle="repuestos con faltante según previsión"
          color="#6366f1"
          cols={3}
          posicion={false}
          cargando={cargando}
          error={error}
        />
        <TarjetaRanking
          titulo="Artículos de mayor gasto (último mes)"
          filas={gasto}
          columnas={[
            {
              campo: "Gasto",
              formatoTitulo: (v) => fmt_dinero_corto.format(Number(v)),
              formatoLista: (v) => fmt_dinero.format(Number(v)),
            },
          ]}
          textoSuma="Suma del top 10"
          color="#F54927"
          cargando={cargando}
          error={error}
          posicion={false}
        />
        <TarjetaRanking
          titulo="Artículos de mayor consumo (último mes)"
          filas={consumo}
          columnas={[
            {
              campo: "Cantidad",
              formatoTitulo: (v) => fmt_spark.format(Number(v)),
            },
          ]}
          textoSuma="Unidades del top 10"
          color="#f59e0b"
          cargando={cargando}
          posicion={false}
          error={error}
        />
        <TarjetaMicro
          titulo="Críticos sin stock"
          cols={1}
          alto={100}
          valor={crit.length}
          detalle="repuestos críticos con existencia 0"
          tono={crit.length > 0 ? "mal" : "ok"}
          cargando={cargando}
          error={error}
        >
          <ul className="tarjeta-lista">
            {crit.slice(0, 3).map((c) => (
              <li key={c.IDRepuesto}>
                {c.Codigo} · {c.Descripcion}
              </li>
            ))}
          </ul>
        </TarjetaMicro>
      </div>
    </div>
  );
}
