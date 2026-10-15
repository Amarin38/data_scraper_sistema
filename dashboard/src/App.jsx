import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout.jsx";
import IndicesConsumoPage from "./modulos/indices-consumo/IndicesConsumoPage.jsx";
import PrevisionPage from "./modulos/prevision/PrevisionPage.jsx";
import DuracionRepuestosPage from "./modulos/duracion-repuestos/DuracionRepuestosPage.jsx";
import { indices_ep, previsiones_ep, duraciones_ep } from "./constants.js";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="*" element={<Navigate to={indices_ep} replace />} />
        <Route path="/" element={<Navigate to={indices_ep} replace />} />
        <Route path={indices_ep} element={<IndicesConsumoPage />} />
        <Route path={previsiones_ep} element={<PrevisionPage />} />
        <Route path={duraciones_ep} element={<DuracionRepuestosPage />} />
      </Route>
    </Routes>
  );
}
