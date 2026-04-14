export default function ProgressLog({ steps }) {
  return (
    <div className="progress-log">
      {steps.map((msg, i) => (
        <p key={i} className="progress-step">
          <span>{i === steps.length - 1 ? "→" : "✓"}</span>
          {msg}
        </p>
      ))}
    </div>
  );
}
