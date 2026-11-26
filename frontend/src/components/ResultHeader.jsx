import { useState } from "react";

const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

export default function ResultHeader({ result }) {
  const [copied, setCopied] = useState(false);
  const json = JSON.stringify(result.data, null, 2);

  async function copy() {
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard blocked: the Download button still works */
    }
  }

  function download() {
    const url = URL.createObjectURL(new Blob([json], { type: "application/json" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `${result.filename.replace(/\.[^.]+$/, "")}_extracted.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="result-head">
      <div>
        <h2>{result.filename}</h2>
        <p className="tags">
          <span className="tag">Level: {cap(result.level)}</span>
          <span className="tag">Summary: {cap(result.style)}</span>
          {result.focus && <span className="tag">Focus: {result.focus.join(", ")}</span>}
        </p>
      </div>
      <div className="actions">
        <button type="button" className="secondary" onClick={copy}>{copied ? "Copied" : "Copy JSON"}</button>
        <button type="button" className="secondary" onClick={download}>Download JSON</button>
      </div>
    </div>
  );
}
