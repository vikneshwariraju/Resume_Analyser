import { useEffect, useState } from "react";

export default function LoadingState() {
  const [sec, setSec] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setSec((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const stage = sec < 3 ? "Reading the document" : sec < 9 ? "Writing the summary" : "Extracting and checking the fields";

  return (
    <div className="loading" role="status">
      <p className="loading-stage">
        <span className="spinner dark" aria-hidden="true" />
        {stage}
      </p>
      {sec >= 20 && (
        <p className="muted">This is taking longer than usual. The AI service may be busy, so the server is retrying.</p>
      )}
      <div className="skeleton-overview" aria-hidden="true">
        <div className="sk sk-ring" />
        <div className="sk-lines">
          <div className="sk sk-line w90" />
          <div className="sk sk-line w100" />
          <div className="sk sk-line w75" />
          <div className="sk sk-line w60" />
        </div>
      </div>
      <div className="skeleton-lower" aria-hidden="true">
        <div className="sk sk-block" />
        <div className="sk sk-block short" />
      </div>
    </div>
  );
}
