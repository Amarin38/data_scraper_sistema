import { useCallback, useEffect, useState } from "react";

const CLAVE = "inicio.anchos"; // { idTarjeta: columnas } — solo las que el usuario fijó

const leer = () => {
  try {
    return JSON.parse(localStorage.getItem(CLAVE)) ?? {};
  } catch {
    return {};
  }
};

/** Anchos fijos de las tarjetas de Inicio, guardados en este navegador. `null` = automático. */
export function useAnchos() {
  const [anchos, setAnchos] = useState(leer);

  useEffect(() => {
    try {
      localStorage.setItem(CLAVE, JSON.stringify(anchos));
    } catch {
      /* sin almacenamiento: se usa solo en memoria */
    }
  }, [anchos]);

  const fijar = useCallback((id, columnas) => {
    setAnchos((previo) => {
      const sig = { ...previo };
      if (columnas == null) delete sig[id];
      else sig[id] = columnas;
      return sig;
    });
  }, []);

  return [anchos, fijar];
}
