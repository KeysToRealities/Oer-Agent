function ScoreBar({ label, score }) {
  const pct = (score / 5) * 100;
  const color = score >= 4 ? "#22c55e" : score >= 3 ? "#f59e0b" : "#ef4444";

  return (
    <div className="score-row">
      <span className="score-label">{label}</span>
      <div className="score-track">
        <div className="score-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="score-value">{score.toFixed(1)}</span>
    </div>
  );
}

export default function ResourceCard({ resource }) {
  return (
    <div className="resource-card">
      <div className="card-header">
        <a href={resource.url} target="_blank" rel="noopener noreferrer">
          <h3>{resource.title}</h3>
        </a>
        <div className="badges">
          <span className="badge source">{resource.source}</span>
          {resource.resource_type && (
            <span className="badge type">{resource.resource_type}</span>
          )}
          <span className="badge license">{resource.license}</span>
        </div>
      </div>

      {resource.description && (
        <p className="description">{resource.description}</p>
      )}

      {resource.explanation && (
        <p className="explanation">{resource.explanation}</p>
      )}

      {resource.total_score !== undefined && (
        <div className="scores">
          {resource.has_rating ? (
            <ScoreBar label="Quality" score={resource.quality_score} />
          ) : (
            <p className="no-rating">Quality: No user ratings available</p>
          )}
          <ScoreBar label="Accessibility" score={resource.accessibility_score} />
          <div className="total-score">
            Accessibility: <strong>{resource.accessibility_score.toFixed(1)} / 5.0</strong>
          </div>
        </div>
      )}
    </div>
  );
}
