import { useEffect, Suspense } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
  const { pathname } = useLocation();
  useEffect(() => {
    const seccion = pathname.split("/")[1];
    const nombre = seccion ? seccion.replace(/[-_]/g, " ") : "";
    document.title = nombre
      ? `${nombre[0].toUpperCase()}${nombre.slice(1)} · Estadísticas Dota`
      : "Estadísticas Dota";
  }, [pathname]);

  return (
    <div className="layout">
      <Navbar />
      <main>
        <Suspense fallback={null}>
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
}
