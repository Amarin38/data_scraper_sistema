import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout.jsx";
import RepuestosPage from "./modulos/repuestos/RepuestosPage.jsx";
import { repuestos_ep } from "./constants.js";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="*" element={<Navigate to={repuestos_ep} replace />} />
        <Route path="/" element={<Navigate to={repuestos_ep} replace />} />
        <Route path={repuestos_ep} element={<RepuestosPage />} />
      </Route>
    </Routes>
  );
}
