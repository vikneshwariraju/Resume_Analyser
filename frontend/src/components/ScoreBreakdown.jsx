import { FIELD_LABELS } from "./UploadPanel";

const STATUS_TEXT = { complete: "Complete", partial: "Partial", missing: "Missing" };

export default function ScoreBreakdown({ completeness }) {
  return (
    <section className="block" aria-labelledby="breakdown-title">
      <h3 id="breakdown-title">Score breakdown</h3>
      <p className="muted breakdown-note">
        Each field has a weight. It earns the full weight when everything expected is present, part of it when some
        details are missing, and nothing when it was not found.
      </p>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Field</th>
              <th scope="col">Weight</th>
              <th scope="col">Result</th>
            </tr>
          </thead>
          <tbody>
            {completeness.fields.map((f) => (
              <tr key={f.field}>
                <th scope="row">
                  {FIELD_LABELS[f.field] || f.field}
                  <span className="cell-note">{f.note}</span>
                </th>
                <td>{f.weight}</td>
                <td className={`status ${f.status}`}>{STATUS_TEXT[f.status]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
