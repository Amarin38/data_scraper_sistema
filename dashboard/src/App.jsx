import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout.jsx";
import InicioPage from "./modulos/inicio/InicioPage.jsx";
import RepuestosPage from "./modulos/repuestos/RepuestosPage.jsx";
import FichaStockPage from "./modulos/ficha_stock/FichaStockPage.jsx";
import ExistenciaStockPage from "./modulos/existencia_stock/ExistenciaStockPage.jsx";
import ParqueMovilPage from "./modulos/parque_movil/ParqueMovilPage.jsx";

import {
  inicio_ep,
  repuestos_ep,
  ficha_stock_ep,
  existencia_stock_ep,
  parque_movil_ep,
} from "./constants.js";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="*" element={<Navigate to={inicio_ep} replace />} />
        <Route path="/" element={<Navigate to={inicio_ep} replace />} />
        <Route path={inicio_ep} element={<InicioPage />} />
        <Route path={repuestos_ep} element={<RepuestosPage />} />
        <Route path={ficha_stock_ep} element={<FichaStockPage />} />
        <Route path={existencia_stock_ep} element={<ExistenciaStockPage />} />
        <Route path={parque_movil_ep} element={<ParqueMovilPage />} />
      </Route>
    </Routes>
  );
}
