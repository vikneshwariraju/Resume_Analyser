// Renders the summary text. Bullet-style summaries come back as "- item" lines, so we turn those into a list.
function clean(line) {
  return line.replace(/\*\*/g, "").trim();
}

export default function SummaryView({ summary }) {
  const blocks = [];
  let list = null;

  summary.split("\n").forEach((raw) => {
    const line = raw.trim();
    if (!line) {
      list = null;
      return;
    }
    if (/^[-*•]\s+/.test(line)) {
      if (!list) {
        list = { type: "ul", items: [] };
        blocks.push(list);
      }
      list.items.push(clean(line.replace(/^[-*•]\s+/, "")));
    } else {
      list = null;
      const text = clean(line.replace(/^#+\s*/, ""));
      const isHeading = /^\*\*.+\*\*:?$/.test(line) || /^#+\s/.test(line) || /^[A-Za-z ]{3,30}:$/.test(line);
      blocks.push({ type: isHeading ? "h" : "p", text: text.replace(/:$/, "") });
    }
  });

  return (
    <section className="block" aria-labelledby="summary-title">
      <h3 id="summary-title">Summary</h3>
      <div className="summary">
        {blocks.map((b, i) =>
          b.type === "ul" ? (
            <ul key={i}>{b.items.map((it, j) => <li key={j}>{it}</li>)}</ul>
          ) : b.type === "h" ? (
            <h4 key={i}>{b.text}</h4>
          ) : (
            <p key={i}>{b.text}</p>
          )
        )}
      </div>
    </section>
  );
}
