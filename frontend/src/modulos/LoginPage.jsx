import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";
import { inicio_ep } from "../constants.js";

export default function LoginPage() {
  const { usuario, login } = useAuth();
  const location = useLocation();
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);

  if (usuario)
    return <Navigate to={location.state?.desde ?? inicio_ep} replace />;

  async function enviar(e) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await login(user, password); // al setear usuario, el Navigate de arriba redirige
    } catch (err) {
      setError(err.message);
      setEnviando(false);
    }
  }

  return (
    <div className="login">
      <form className="login-caja" onSubmit={enviar}>
        <h1>Estadísticas</h1>
        <label className="modal-campo">
          <span>Usuario</span>
          <input
            value={user}
            onChange={(e) => setUser(e.target.value)}
            autoComplete="username"
            autoFocus
            required
          />
        </label>
        <label className="modal-campo">
          <span>Contraseña</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error && <p className="modal-error">{error}</p>}
        <button className="login-enviar" disabled={enviando}>
          {enviando ? "Ingresando…" : "Ingresar"}
        </button>
      </form>
    </div>
  );
}
