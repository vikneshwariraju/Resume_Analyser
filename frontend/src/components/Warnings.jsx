export default function Warnings({ warnings }) {
  return (
    <section className="warnings" aria-labelledby="warnings-title">
      <h3 id="warnings-title">Needs a second look</h3>
      <ul>
        {warnings.map((w, i) => <li key={i}>{w}</li>)}
      </ul>
    </section>
  );
}
