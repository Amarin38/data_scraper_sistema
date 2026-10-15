export default function SelectConjuntos({ conjuntos, conjunto, setConjunto }) {
  return (
    <>
      <select value={conjunto} onChange={(e) => setConjunto(e.target.value)}>
        <option value="">Todos</option>
        {conjuntos.map((conj) => (
          <option key={conj} value={conj}>
            {conj}
          </option>
        ))}
      </select>
    </>
  );
}
