import { FIELD_LABELS } from "./UploadPanel";

const STATUS_TEXT = { complete: "Complete", partial: "Partial", missing: "Missing" };

export default function CompletenessBar({ completeness }) {
  const { score, label, fields } = completeness;

  return (
    <section className="block" aria-labelledby="completeness-title">
      <div className="comp-top">
        <div>
          <h3 id="completeness-title">Completeness</h3>
          <p className="muted">Based on the {fields.length} fields in this analysis.</p>
        </div>
        <div className="comp-score">
          <strong>{score}%</strong>
          <span>{label}</span>
        </div>
      </div>

      <div
        className="meter"
        role="progressbar"
        aria-label="Completeness"
        aria-valuenow={score}
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <div className={`meter-fill${score < 60 ? " low" : ""}`} style={{ width: `${score}%` }} />
      </div>

      <details className="how">
        <summary>How the score is calculated</summary>
        <p className="muted">
          Every field has a weight. A field earns its full weight when everything expected is present, part of it when
          some details are missing, and nothing when it was not found. The score is the points earned out of the points
          available for the fields in this analysis.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Field</th>
                <th scope="col">Weight</th>
                <th scope="col">Result</th>
                <th scope="col">Detail</th>
              </tr>
            </thead>
            <tbody>
              {fields.map((f) => (
                <tr key={f.field}>
                  <th scope="row">{FIELD_LABELS[f.field] || f.field}</th>
                  <td>{f.weight}</td>
                  <td className={`status ${f.status}`}>{STATUS_TEXT[f.status]}</td>
                  <td>{f.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}
