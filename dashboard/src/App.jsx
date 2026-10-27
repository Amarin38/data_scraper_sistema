import { Routes, Route, Navigate, Outlet, useLocation } from "react-router-dom";
import Layout from "./components/layout/Layout.jsx";
import LoginPage from "./modulos/LoginPage.jsx";
import { useAuth } from "./auth/AuthContext.jsx";
import { lazy, Suspense } from "react";

const InicioPage = lazy(() => import("./modulos/InicioPage.jsx"));
const RepuestosPage = lazy(
  () => import("./modulos/repuestos/RepuestosPage.jsx"),
);
const FichaStockPage = lazy(
  () => import("./modulos/ficha_stock/FichaStockPage.jsx"),
);
const ExistenciaStockPage = lazy(
  () => import("./modulos/existencia_stock/ExistenciaStockPage.jsx"),
);
const ParqueMovilPage = lazy(
  () => import("./modulos/parque_movil/ParqueMovilPage.jsx"),
);

import {
  inicio_ep,
  repuestos_ep,
  ficha_stock_ep,
  existencia_stock_ep,
  parque_movil_ep,
} from "./constants.js";

function Protegida() {
  const { usuario, cargando } = useAuth();
  const location = useLocation();

  if (cargando) return null;
  if (!usuario) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ desde: location.pathname + location.search }}
      />
    );
  }
  return <Outlet />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<Protegida />}>
        <Route element={<Layout />}>
          <Route path="*" element={<Navigate to={inicio_ep} replace />} />
          <Route path="/" element={<Navigate to={inicio_ep} replace />} />
          <Route path={inicio_ep} element={<InicioPage />} />
          <Route path={repuestos_ep} element={<RepuestosPage />} />
          <Route path={ficha_stock_ep} element={<FichaStockPage />} />
          <Route path={existencia_stock_ep} element={<ExistenciaStockPage />} />
          <Route path={parque_movil_ep} element={<ParqueMovilPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
