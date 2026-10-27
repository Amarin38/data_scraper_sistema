import { useEffect, useState } from "react";
import TarjetaMicro from "../components/grafico/TarjetaMicro.jsx";
import Sparkline from "../components/grafico/Sparkline.jsx";
import ListaImportar from "../components/grafico/ListarImportar.jsx";
import { datos_rapidos_ep, fmt_spark } from "../constants.js";
import { get, getCacheado } from "../api/client.js";

const getDatosRapidos = () => getCacheado(datos_rapidos_ep);

const aSerie = (filas, x, y, extra) =>
  filas.map((f) => ({
    x: f[x],
    y: Number(f[y]),
    extra: extra ? f[extra] : null,
  }));

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
  const top = datos?.mayor_stock ?? [];
  const crit = datos?.crit_sin_exist ?? [];
  const imp = datos?.importar ?? [];

  return (
    <div className="inicio">
      <header className="inicio-cabecera">
        <h1>Estadísticas rápidas</h1>
        <p>Resumen de estadísticas rápidas del sistema.</p>
      </header>
      <div className="tarjetas">
        <TarjetaMicro
          titulo="Próximos a importar (previsión 3 meses)"
          valor={imp.length}
          detalle="repuestos con faltante según previsión"
          cols={3}
          alto={435}
          cargando={cargando}
          error={error}
          vacio={!cargando && !error && imp.length === 0}
        >
          <ListaImportar filas={imp} />
        </TarjetaMicro>
        <TarjetaMicro
          titulo="Articulos de Mayor consumo (último mes)"
          cols={2}
          alto={350}
          valor={top[0] ? fmt_spark.format(Number(top[0].Cantidad)) : null}
          detalle={top[0] ? `${top[0].Codigo} · ${top[0].Descripcion}` : null}
          cargando={cargando}
          error={error}
          vacio={!cargando && !error && top.length === 0}
        >
          <Sparkline
            datos={aSerie(top, "Codigo", "Cantidad", "Descripcion")}
            tipo="bar"
            color="#f59e0b"
            alto={350}
          />
        </TarjetaMicro>

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
