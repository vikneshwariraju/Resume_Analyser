const R = 56;
const C = 2 * Math.PI * R;

export default function CompletenessBar({ completeness }) {
  const { score, label, fields } = completeness;
  const tone = score >= 85 ? "good" : score >= 60 ? "mid" : "low";

  return (
    <section className={`score-card ${tone}`} aria-labelledby="completeness-title">
      <h3 id="completeness-title">Completeness</h3>
      <div className="ring" role="progressbar" aria-label="Completeness" aria-valuenow={score} aria-valuemin="0" aria-valuemax="100">
        <svg viewBox="0 0 140 140" aria-hidden="true">
          <circle className="ring-track" cx="70" cy="70" r={R} />
          <circle className="ring-fill" cx="70" cy="70" r={R} style={{ "--c": C, "--target": C * (1 - score / 100) }} />
        </svg>
        <span className="ring-num">
          {score}
          <small>%</small>
        </span>
      </div>
      <p className="score-label">{label}</p>
      <p className="muted">Based on {fields.length} fields</p>
    </section>
  );
}
