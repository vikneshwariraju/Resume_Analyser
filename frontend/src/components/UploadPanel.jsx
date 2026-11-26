import { useState } from "react";

const STYLE_LABELS = { brief: "Brief", detailed: "Detailed", bullets: "Bullet points" };
const LEVEL_LABELS = {
  basic: ["Basic", "Name, email, skills"],
  standard: ["Standard", "Adds phone, education, experience"],
  detailed: ["Detailed", "Adds projects, certifications, links"],
};
export const FIELD_LABELS = {
  name: "Name",
  email: "Email",
  phone: "Phone",
  skills: "Skills",
  education: "Education",
  experience: "Experience",
  projects: "Projects",
  certifications: "Certifications",
  links: "Links",
};

export default function UploadPanel({
  options, samples, file, sample, style, level, focus, loading, stale,
  onFile, onClearFile, onSample, onStyle, onLevel, onToggleFocus, onSubmit,
}) {
  const [dragging, setDragging] = useState(false);
  const ready = Boolean(options);
  const levelFields = ready ? options.levels[level] : [];

  return (
    <aside className="panel" aria-label="Analysis setup">
      <fieldset disabled={!ready || loading}>
        <legend>Resume</legend>

        <label
          className={`drop${dragging ? " dragging" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); onFile(e.dataTransfer.files[0]); }}
        >
          <input type="file" accept=".pdf,.txt" onChange={(e) => onFile(e.target.files[0])} />
          <span className="drop-title">{file ? "Choose a different file" : "Choose a file or drop it here"}</span>
          <span className="muted">PDF or TXT, up to 5 MB</span>
        </label>

        {file && (
          <div className="file-chip">
            <span className="file-name">{file.name}</span>
            <button type="button" className="link-button" onClick={onClearFile}>Remove</button>
          </div>
        )}

        {samples.length > 0 && (
          <div className="field">
            <label htmlFor="sample">Or try a sample</label>
            <select id="sample" value={sample} onChange={(e) => onSample(e.target.value)}>
              <option value="">No sample selected</option>
              {samples.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}
      </fieldset>

      <fieldset disabled={!ready || loading}>
        <legend>Summary style</legend>
        <div className="segmented">
          {ready && options.styles.map((s) => (
            <label key={s} className={style === s ? "on" : ""}>
              <input type="radio" name="style" value={s} checked={style === s} onChange={() => onStyle(s)} />
              {STYLE_LABELS[s] || s}
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset disabled={!ready || loading}>
        <legend>Analysis level</legend>
        <div className="levels">
          {ready && Object.keys(options.levels).map((l) => (
            <label key={l} className={level === l ? "on" : ""}>
              <input type="radio" name="level" value={l} checked={level === l} onChange={() => onLevel(l)} />
              <span className="level-name">{(LEVEL_LABELS[l] || [l])[0]}</span>
              <span className="muted">{(LEVEL_LABELS[l] || ["", ""])[1]}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset disabled={!ready || loading}>
        <legend>Focus on specific fields</legend>
        <p className="muted hint">Optional. Leave all unchecked to include every field at this level.</p>
        <div className="checks">
          {levelFields.map((f) => (
            <label key={f}>
              <input type="checkbox" checked={focus.includes(f)} onChange={() => onToggleFocus(f)} />
              {FIELD_LABELS[f] || f}
            </label>
          ))}
        </div>
      </fieldset>

      <button type="button" className="primary" onClick={onSubmit} disabled={!ready || loading}>
        {loading && <span className="spinner" aria-hidden="true" />}
        {loading ? "Analyzing…" : stale ? "Update results" : "Analyze resume"}
      </button>
    </aside>
  );
}
