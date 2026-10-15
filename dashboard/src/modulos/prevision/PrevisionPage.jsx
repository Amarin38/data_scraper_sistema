import Grafico from "../../components/grafico/Grafico";
import { useEffect, useState, useMemo } from "react";
import { getPrevisiones, getConjuntos } from "./api";

export default function PrevisionPage() {
  const option = useMemo(() => {});

  return <Grafico option={option} />;
}
