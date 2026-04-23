const SOURCE_LABELS = {
  ALG: "Affordable Learning Georgia",
};

export default function FilterBar({ results, filters, onFilter, filteredCount }) {
  const sources = [...new Set(results.map((r) => r.source).filter(Boolean))].sort();
  const licenses = [...new Set(results.map((r) => r.license).filter(Boolean))].sort();
  const types = [...new Set(results.map((r) => r.resource_type).filter(Boolean))].sort();

  const hasActive =
    filters.source ||
    filters.license ||
    filters.resourceType ||
    filters.minScore ||
    filters.sort !== "score_desc";

  function update(key, value) {
    onFilter({ ...filters, [key]: value });
  }

  function reset() {
    onFilter({ source: "", license: "", resourceType: "", minScore: "", sort: "score_desc" });
  }

  return (
    <div className="filter-bar">
      <div className="filter-controls">
        <select
          className="filter-select"
          value={filters.source}
          onChange={(e) => update("source", e.target.value)}
        >
          <option value="">All Sources</option>
          {sources.map((s) => (
            <option key={s} value={s}>
              {SOURCE_LABELS[s] ?? s}
            </option>
          ))}
        </select>

        <select
          className="filter-select"
          value={filters.license}
          onChange={(e) => update("license", e.target.value)}
        >
          <option value="">All Licenses</option>
          {licenses.map((l) => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>

        {types.length > 0 && (
          <select
            className="filter-select"
            value={filters.resourceType}
            onChange={(e) => update("resourceType", e.target.value)}
          >
            <option value="">All Types</option>
            {types.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        )}

        <select
          className="filter-select"
          value={filters.minScore}
          onChange={(e) => update("minScore", e.target.value)}
        >
          <option value="">Any Score</option>
          <option value="3">3.0+</option>
          <option value="4">4.0+</option>
          <option value="4.5">4.5+</option>
        </select>

        <select
          className="filter-select"
          value={filters.sort}
          onChange={(e) => update("sort", e.target.value)}
        >
          <option value="score_desc">Score: High to Low</option>
          <option value="score_asc">Score: Low to High</option>
          <option value="title_asc">Title: A–Z</option>
        </select>
      </div>

      <div className="filter-meta">
        <span className="filter-count">
          {filteredCount} result{filteredCount !== 1 ? "s" : ""}
        </span>
        {hasActive && (
          <button className="filter-clear" onClick={reset}>
            Clear filters
          </button>
        )}
      </div>
    </div>
  );
}
