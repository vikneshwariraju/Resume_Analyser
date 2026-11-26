const SHOWN = 8;

export default function SkillsChart({ categories }) {
  if (!categories) {
    return (
      <section className="block" aria-labelledby="chart-title">
        <h3 id="chart-title">Skills by category</h3>
        <p className="muted">No skills were found in the document, so there is nothing to chart.</p>
      </section>
    );
  }

  const max = Math.max(...categories.map((c) => c.count));
  const total = categories.reduce((sum, c) => sum + c.count, 0);

  return (
    <section className="block" aria-labelledby="chart-title">
      <h3 id="chart-title">Skills by category</h3>
      <p className="muted chart-note">
        {total} skills grouped with keyword rules. Anything not recognised is listed under Other.
      </p>
      <ul className="bars">
        {categories.map((c) => (
          <li key={c.category}>
            <div className="bar-head">
              <span>{c.category}</span>
              <span className="bar-count">{c.count}</span>
            </div>
            <div className="track" role="img" aria-label={`${c.category}: ${c.count} of ${total} skills`}>
              <div className="fill" style={{ width: `${(c.count / max) * 100}%` }} />
            </div>
            <p className="muted bar-skills">
              {c.skills.slice(0, SHOWN).join(", ")}
              {c.skills.length > SHOWN ? `, and ${c.skills.length - SHOWN} more` : ""}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
