export default function Tabla({
  nombreTabla,
  nombreScroll,
  columnas,
  filas = [],
  orden,
  onOrdenar,
  pkFila,
  seleccionada,
  onSeleccionar,
}) {
  const claseAlin = (c) => (c.alinear ? `alin-${c.alinear}` : "");
  return (
    <>
      <div className={nombreScroll}>
        <table className={nombreTabla}>
          <thead>
            <tr>
              {columnas.map((col) => (
                <th
                  key={col.campo}
                  className={claseAlin(col)}
                  style={{
                    width: col.ancho,
                    cursor: col.claveOrden ? "pointer" : "default",
                  }}
                  onClick={
                    col.claveOrden ? () => onOrdenar(col.claveOrden) : undefined
                  }
                >
                  {col.titulo}
                  {orden?.campo === col.claveOrden && (
                    <span className={`flecha ${orden.dir}`} />
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filas.map((fil) => {
              const id = fil[pkFila];
              return (
                <tr
                  key={id}
                  className={id === seleccionada ? "sel" : ""}
                  onClick={() => onSeleccionar?.(fil)}
                >
                  {columnas.map((col) => (
                    <td key={col.campo} className={claseAlin(col)}>
                      {col.render ? col.render(fil) : fil[col.campo]}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
