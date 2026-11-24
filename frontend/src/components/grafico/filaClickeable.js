// props para hacer una fila clickeable y accesible con teclado
export const filaClickeable = (fila, onSeleccionar) =>
  onSeleccionar
    ? {
        role: "button",
        tabIndex: 0,
        onClick: () => onSeleccionar(fila),
        onKeyDown: (e) => e.key === "Enter" && onSeleccionar(fila),
      }
    : {};
