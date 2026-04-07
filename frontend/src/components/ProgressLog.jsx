export default function ProgressLog({ steps }) {
  return (
    <div className="progress-log">
      {steps.map((msg, i) => (
        <p key={i} className="progress-step">
          {i === steps.length - 1 ? "→ " : "✓ "}
          {msg}
        </p>
      ))}
    </div>
  );
}
