import { FIELD_LABELS } from "./UploadPanel";

function Chips({ items }) {
  return (
    <ul className="chips">
      {items.map((s, i) => <li key={i}>{s}</li>)}
    </ul>
  );
}

function renderValue(field, value) {
  if (typeof value === "string") return <p>{value}</p>;

  if (field === "skills" || field === "certifications") return <Chips items={value} />;
  if (field === "links") return <ul className="plain">{value.map((v, i) => <li key={i}>{v}</li>)}</ul>;

  if (field === "education") {
    return (
      <ul className="entries">
        {value.map((e, i) => (
          <li key={i}>
            <strong>{e.degree || "Degree not found"}</strong>
            <span>{[e.institution, e.year, e.score].filter(Boolean).join(", ") || "No further details"}</span>
          </li>
        ))}
      </ul>
    );
  }

  if (field === "experience") {
    return (
      <ul className="entries">
        {value.map((e, i) => (
          <li key={i}>
            <strong>{[e.role, e.company].filter(Boolean).join(" at ") || "Role not found"}</strong>
            {e.duration && <span>{e.duration}</span>}
            {e.description && <span>{e.description}</span>}
          </li>
        ))}
      </ul>
    );
  }

  if (field === "projects") {
    return (
      <ul className="entries">
        {value.map((p, i) => (
          <li key={i}>
            <strong>{p.name || "Untitled project"}</strong>
            {p.description && <span>{p.description}</span>}
            {p.technologies && <Chips items={p.technologies} />}
          </li>
        ))}
      </ul>
    );
  }

  return <p>{JSON.stringify(value)}</p>;
}

export default function FieldsReview({ data, fields, missing, statuses = [] }) {
  const byField = Object.fromEntries(statuses.map((s) => [s.field, s]));

  return (
    <section className="block sheet" aria-labelledby="fields-title">
      <h3 id="fields-title">Extracted details</h3>
      <dl className="fields">
        {fields.map((f) => {
          const isMissing = missing.includes(f);
          const isPartial = !isMissing && byField[f] && byField[f].status === "partial";
          return (
            <div key={f} className={`row${isMissing ? " missing" : isPartial ? " partial" : ""}`}>
              <dt>{FIELD_LABELS[f] || f}</dt>
              <dd>
                {isMissing ? <p>Not found in the document</p> : renderValue(f, data[f])}
                {isPartial && <p className="partial-note">Incomplete: {byField[f].note}</p>}
              </dd>
            </div>
          );
        })}
      </dl>
    </section>
  );
}
