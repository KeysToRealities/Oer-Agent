export default function ResourceCard({ resource }) {
  return (
    <div className="resource-card">
      <div className="card-header">
        <a href={resource.url} target="_blank" rel="noopener noreferrer">
          <h3>{resource.title}</h3>
        </a>
        <span className="badge source">{resource.source}</span>
        <span className="badge license">{resource.license}</span>
      </div>
      {resource.description && (
        <p className="description">{resource.description}</p>
      )}
      {resource.explanation && (
        <p className="explanation">{resource.explanation}</p>
      )}
    </div>
  );
}
