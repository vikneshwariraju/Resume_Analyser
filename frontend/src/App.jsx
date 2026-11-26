import { useEffect, useRef, useState } from "react";
import { getOptions, getSamples, analyze } from "./api";
import UploadPanel from "./components/UploadPanel";
import SummaryView from "./components/SummaryView";
import FieldsReview from "./components/FieldsReview";
import CompletenessBar from "./components/CompletenessBar";
import SkillsChart from "./components/SkillsChart";
import ScoreBreakdown from "./components/ScoreBreakdown";
import Warnings from "./components/Warnings";
import ResultHeader from "./components/ResultHeader";
import LoadingState from "./components/LoadingState";
import Logo from "./components/Logo";

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
  const resultsRef = useRef(null);

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
    if (window.innerWidth <= 860) resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    try {
      setResult(await analyze({ file, sample, style, level, focus }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <header className="band">
        <div className="band-inner">
          <Logo />
          <div>
            <h1>Resume Analyzer</h1>
            <p>
              Upload a resume to get a summary and structured details. Anything the AI cannot find in the document is
              marked as missing, not guessed.
            </p>
          </div>
        </div>
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
          onClearFile={() => setFile(null)}
          onSample={handleSample}
          onStyle={setStyle}
          onLevel={handleLevel}
          onToggleFocus={toggleFocus}
          onSubmit={handleSubmit}
        />

        <section className="results" aria-live="polite" ref={resultsRef}>
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

          {!options && !error && (
            <div className="notice">Connecting to the server. The first request can take up to a minute.</div>
          )}

          {loading && <LoadingState />}

          {!loading && !result && options && !error && (
            <div className="empty">
              <svg width="72" height="72" viewBox="0 0 72 72" aria-hidden="true">
                <rect x="14" y="8" width="44" height="56" rx="6" fill="#E0F0F2" />
                <path d="M24 24h24M24 34h24M24 44h14" stroke="#0F6C7A" strokeWidth="3" strokeLinecap="round" />
                <circle cx="52" cy="52" r="10" fill="#0F6C7A" />
                <path d="M47.5 52l3 3 5-6" stroke="#fff" strokeWidth="2.4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <h2>Your results will appear here</h2>
              <p>Choose a sample or upload a PDF or TXT file, pick your options, then select Analyze resume.</p>
            </div>
          )}

          {result && (
            <div className="result-stack">
              <ResultHeader result={result} />

              <div className="overview">
                {result.completeness && <CompletenessBar completeness={result.completeness} />}
                <SummaryView summary={result.summary} />
              </div>

              {result.warnings.length > 0 && <Warnings warnings={result.warnings} />}

              <div className="lower">
                <FieldsReview
                  data={result.data}
                  fields={result.fields}
                  missing={result.missing_fields}
                  statuses={result.completeness ? result.completeness.fields : []}
                />
                <div className="side">
                  {result.fields.includes("skills") && result.insights && (
                    <SkillsChart categories={result.insights.skill_categories} />
                  )}
                  {result.completeness && <ScoreBreakdown completeness={result.completeness} />}
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </>
  );
}
