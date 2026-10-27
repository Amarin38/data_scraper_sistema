import { createContext, useContext, useEffect, useState } from "react";
import { get, post, limpiarCache } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  // al abrir la app: ¿hay sesión?
  useEffect(() => {
    get("/auth/yo")
      .then(setUsuario)
      .catch(() => setUsuario(null))
      .finally(() => setCargando(false));
  }, []);

  // cualquier 401 de datos cierra la sesión en el front
  useEffect(() => {
    const salir = () => {
      limpiarCache();
      setUsuario(null);
    };
    window.addEventListener("sesion-expirada", salir);
    return () => window.removeEventListener("sesion-expirada", salir);
  }, []);

  async function login(user, password) {
    setUsuario(await post("/auth/login", { user, password }));
  }

  async function logout() {
    await post("/auth/logout").catch(() => {});
    limpiarCache();
    setUsuario(null);
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
