import { createContext, useContext, useEffect, useState } from "react";
import { get, post, put, limpiarCache } from "../api/client.js";

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

  // tema: el del usuario, y modo día cuando no hay sesión (la pantalla de login siempre es clara)
  useEffect(() => {
    if (cargando) return; // todavía no se sabe quién es: se deja el último
    const tema = usuario?.modo_noche ? "oscuro" : "claro";
    document.documentElement.dataset.tema = tema;
    try {
      localStorage.setItem("tema", tema);
    } catch {
      /* sin almacenamiento: no pasa nada */
    }
  }, [usuario, cargando]);

  async function login(user, password) {
    setUsuario(await post("/auth/login", { user, password }));
  }

  async function logout() {
    await post("/auth/logout").catch(() => {});
    limpiarCache();
    setUsuario(null);
  }

  // se aplica al instante y se guarda en el usuario; si falla, vuelve al valor anterior
  async function cambiarModoNoche(valor) {
    const anterior = !!usuario?.modo_noche;
    setUsuario((u) => (u ? { ...u, modo_noche: valor } : u));
    try {
      await put("/auth/preferencias", { modo_noche: valor });
    } catch {
      setUsuario((u) => (u ? { ...u, modo_noche: anterior } : u));
    }
  }

  return (
    <AuthContext.Provider
      value={{ usuario, cargando, login, logout, cambiarModoNoche }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
