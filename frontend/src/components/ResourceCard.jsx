import { useState } from "react";

const SOURCE_LABELS = {
  ALG: "Affordable Learning Georgia",
};

function displaySource(source) {
  return SOURCE_LABELS[source] ?? source;
}

function ScoreBar({ label, score }) {
  const s = score ?? 0;
  const pct = (s / 5) * 100;
  const color = s >= 4 ? "#22c55e" : s >= 3 ? "#f59e0b" : "#ef4444";

  return (
    <div className="score-row">
      <div className="score-label">
        <span>{label}</span>
        <span className="score-value">{s.toFixed(1)}</span>
      </div>
      <div className="score-track">
        <div className="score-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

function ResourceModal({ resource, onClose }) {
  const hasScores = resource.total_score !== undefined;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close">
          &#10005;
        </button>

        <div className="modal-header">
          <a href={resource.url} target="_blank" rel="noopener noreferrer">
            <h2>{resource.title}</h2>
          </a>
          <div className="badges">
            <span className="badge source">{displaySource(resource.source)}</span>
            {resource.resource_type && (
              <span className="badge type">{resource.resource_type}</span>
            )}
            <span className="badge license">{resource.license}</span>
            {hasScores && (
              <span className="badge overall">
                Overall {(resource.total_score ?? 0).toFixed(1)} / 5.0
              </span>
            )}
          </div>
        </div>

        {resource.description && (
          <p className="description">{resource.description}</p>
        )}
        {resource.explanation && (
          <p className="explanation">{resource.explanation}</p>
        )}

        {hasScores && (
          <div className="scores">
            <ScoreBar label="Relevance"      score={resource.relevance_score} />
            <ScoreBar label="Ped. Value"     score={resource.pedagogical_value_score} />
            <ScoreBar label="Currency"       score={resource.currency_score} />
            <ScoreBar label="Tech Quality"   score={resource.technical_quality_score} />
            <ScoreBar label="Interactivity"  score={resource.interactivity_score} />
            {resource.has_rating
              ? <ScoreBar label="User Rating" score={resource.quality_score} />
              : <div className="no-rating">No user ratings</div>
            }
          </div>
        )}
      </div>
    </div>
  );
}

export default function ResourceCard({ resource }) {
  const [open, setOpen] = useState(false);
  const hasScores = resource.total_score !== undefined;

  const brief = resource.description
    ? resource.description.length > 130
      ? resource.description.slice(0, 130).trimEnd() + "…"
      : resource.description
    : null;

  return (
    <>
      <div className="resource-card resource-card--compact" onClick={() => setOpen(true)}>
        <div className="card-header">
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>{resource.title}</h3>
          </a>
          <div className="badges">
            <span className="badge source">{displaySource(resource.source)}</span>
            {resource.resource_type && (
              <span className="badge type">{resource.resource_type}</span>
            )}
          </div>
        </div>

        {brief && <p className="description description--brief">{brief}</p>}

        {hasScores && (
          <div className="card-score-row">
            <span className="badge overall">
              Overall {(resource.total_score ?? 0).toFixed(1)} / 5.0
            </span>
            <span className="card-details-hint">View details →</span>
          </div>
        )}
      </div>

      {open && <ResourceModal resource={resource} onClose={() => setOpen(false)} />}
    </>
  );
}
