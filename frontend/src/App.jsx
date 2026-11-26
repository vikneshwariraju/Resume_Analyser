import { useEffect, useState } from "react";
import { getOptions, getSamples, analyze } from "./api";
import UploadPanel from "./components/UploadPanel";
import SummaryView from "./components/SummaryView";
import FieldsReview from "./components/FieldsReview";
import CompletenessBar from "./components/CompletenessBar";
import SkillsChart from "./components/SkillsChart";

const MAX_BYTES = 5 * 1024 * 1024;

export default function App() {
  const [options, setOptions] = useState(null);
  const [samples, setSamples] = useState([]);
  const [file, setFile] = useState(null);
  const [sample, setSample] = useState("");
  const [style, setStyle] = useState("brief");
  const [level, setLevel] = useState("standard");
  const [focus, setFocus] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  function loadSetup() {
    setError("");
    Promise.all([getOptions(), getSamples()])
      .then(([o, s]) => {
        setOptions(o);
        setSamples(s.samples);
      })
      .catch((e) => setError(e.message));
  }

  useEffect(loadSetup, []);

  function handleFile(f) {
    if (!f) return;
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["pdf", "txt"].includes(ext)) {
      setError("Unsupported file type. Upload a PDF or TXT file.");
      return;
    }
    if (f.size > MAX_BYTES) {
      setError("File is too large. The limit is 5 MB.");
      return;
    }
    setError("");
    setFile(f);
    setSample("");
  }

  function handleSample(name) {
    setSample(name);
    setFile(null);
    setError("");
  }

  function handleLevel(l) {
    setLevel(l);
    setFocus((current) => current.filter((f) => options.levels[l].includes(f)));
  }

  function toggleFocus(field) {
    setFocus((current) => (current.includes(field) ? current.filter((f) => f !== field) : [...current, field]));
  }

  async function handleSubmit() {
    if (!file && !sample) {
      setError("Choose a sample or upload a file first.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await analyze({ file, sample, style, level, focus }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="masthead">
        <h1>Resume Analyzer</h1>
        <p>
          Upload a resume to get a summary and structured details. Anything the AI cannot find in the document is
          marked as missing, not guessed.
        </p>
      </header>

      <main className="layout">
        <UploadPanel
          options={options}
          samples={samples}
          file={file}
          sample={sample}
          style={style}
          level={level}
          focus={focus}
          loading={loading}
          onFile={handleFile}
          onSample={handleSample}
          onStyle={setStyle}
          onLevel={handleLevel}
          onToggleFocus={toggleFocus}
          onSubmit={handleSubmit}
        />

        <section className="results" aria-live="polite">
          {error && (
            <div className="notice error" role="alert">
              <p>{error}</p>
              {!options && (
                <button type="button" className="link-button" onClick={loadSetup}>
                  Try again
                </button>
              )}
            </div>
          )}

          {!options && !error && <div className="notice">Connecting to the server. The first request can take up to a minute.</div>}

          {loading && <div className="notice">Reading the document and asking the AI. This usually takes 10 to 20 seconds.</div>}

          {!loading && !result && options && !error && (
            <div className="empty">
              <h2>Your results will appear here</h2>
              <p>Choose a sample or upload a PDF or TXT file, pick your options, then select Analyze resume.</p>
            </div>
          )}

          {result && (
            <>
              <div className="result-head">
                <h2>{result.filename}</h2>
                <p className="muted">
                  Analysis level: {result.level}. Summary style: {result.style}.
                </p>
              </div>
              {result.completeness && <CompletenessBar completeness={result.completeness} />}
              <SummaryView summary={result.summary} />
              {result.fields.includes("skills") && result.insights && (
                <SkillsChart categories={result.insights.skill_categories} />
              )}
              <FieldsReview
                data={result.data}
                fields={result.fields}
                missing={result.missing_fields}
                warnings={result.warnings}
                statuses={result.completeness ? result.completeness.fields : []}
                filename={result.filename}
              />
            </>
          )}
        </section>
      </main>
    </div>
  );
}
