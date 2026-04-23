import { useState } from "react";
import SearchBar from "./components/SearchBar";
import ProgressLog from "./components/ProgressLog";
import ResourceCard from "./components/ResourceCard";
import FilterBar from "./components/FilterBar";
import "./App.css";

const PAGE_SIZE = 4;

function Pagination({ page, total, onPage }) {
  const pages = Math.ceil(total / PAGE_SIZE);
  if (pages <= 1) return null;

  return (
    <div className="pagination">
      <button onClick={() => onPage(page - 1)} disabled={page === 1}>
        &#8592;
      </button>
      {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
        <button
          key={p}
          onClick={() => onPage(p)}
          className={p === page ? "active" : ""}
        >
          {p}
        </button>
      ))}
      <button onClick={() => onPage(page + 1)} disabled={page === pages}>
        &#8594;
      </button>
    </div>
  );
}

function App() {
  const [steps, setSteps] = useState([]);
  const [results, setResults] = useState([]);
  const [phase, setPhase] = useState("idle"); // 'idle' | 'loading' | 'done'
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    source: "", license: "", resourceType: "", minScore: "", sort: "score_desc",
  });

  function handleSearch(course) {
    setSteps([]);
    setResults([]);
    setPage(1);
    setQuery(course);
    setFilters({ source: "", license: "", resourceType: "", minScore: "", sort: "score_desc" });
    setPhase("loading");

    const es = new EventSource(
      `http://localhost:5000/api/search?course=${encodeURIComponent(course)}`
    );

    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setSteps((prev) => [...prev, data.message]);

      if (data.results) {
        setResults(data.results);
        setPhase("done");
        es.close();
      }
    };

    es.onerror = () => {
      setSteps((prev) => [...prev, "Something went wrong. Please try again."]);
      setPhase("done");
      es.close();
    };
  }

  function handleBack() {
    setPhase("idle");
    setSteps([]);
    setResults([]);
    setQuery("");
    setPage(1);
    setFilters({ source: "", license: "", resourceType: "", minScore: "", sort: "score_desc" });
  }

  function handleFilter(newFilters) {
    setFilters(newFilters);
    setPage(1);
  }

  const filteredResults = results
    .filter((r) => !filters.source || r.source === filters.source)
    .filter((r) => !filters.license || r.license === filters.license)
    .filter((r) => !filters.resourceType || r.resource_type === filters.resourceType)
    .filter((r) => !filters.minScore || (r.total_score ?? 0) >= parseFloat(filters.minScore))
    .sort((a, b) => {
      if (filters.sort === "score_asc") return (a.total_score ?? 0) - (b.total_score ?? 0);
      if (filters.sort === "title_asc") return a.title.localeCompare(b.title);
      return (b.total_score ?? 0) - (a.total_score ?? 0);
    });

  const pageResults = filteredResults.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const isActive = phase !== "idle";

  return (
    <div className={`app${isActive ? " app--active" : ""}`}>
      <div className={`hero-section${isActive ? " hero-section--compact" : ""}`}>
        <h1>OER Agent</h1>
        {!isActive && (
          <>
            <p className="subtitle">Find open educational resources for your course</p>
            <SearchBar onSearch={handleSearch} loading={phase === "loading"} />
          </>
        )}
      </div>

      {phase === "loading" && (
        <div className="activity-area">
          <ProgressLog steps={steps} />
        </div>
      )}

      {phase === "done" && (
        <div className="results-area">
          <div className="results-header">
            <button className="back-btn" onClick={handleBack}>
              &#8592; Back
            </button>
            <p className="results-label">
              Resources found for <strong>{query}</strong>
            </p>
          </div>
          <FilterBar
            results={results}
            filters={filters}
            onFilter={handleFilter}
            filteredCount={filteredResults.length}
          />
          <div className="results-grid">
            {pageResults.length > 0 ? (
              pageResults.map((r, i) => <ResourceCard key={i} resource={r} />)
            ) : (
              <p className="no-results">No resources match the selected filters.</p>
            )}
          </div>
          <Pagination page={page} total={filteredResults.length} onPage={setPage} />
        </div>
      )}
      <footer className="site-footer">
        Powered by <span className="footer-claude">Claude</span>
      </footer>
    </div>
  );
}

export default App;
