import { useState } from "react";
import SearchBar from "./components/SearchBar";
import ProgressLog from "./components/ProgressLog";
import ResourceCard from "./components/ResourceCard";
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
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  function handleSearch(course) {
    setSteps([]);
    setResults([]);
    setLoading(true);
    setPage(1);

    const es = new EventSource(
      `http://localhost:5000/api/search?course=${encodeURIComponent(course)}`
    );

    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setSteps((prev) => [...prev, data.message]);

      if (data.results) {
        setResults(data.results);
        setLoading(false);
        es.close();
      }
    };

    es.onerror = () => {
      setSteps((prev) => [...prev, "Something went wrong. Please try again."]);
      setLoading(false);
      es.close();
    };
  }

  const pageResults = results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="app">
      <h1>OER Agent</h1>
      <p className="subtitle">Find open educational resources for your course</p>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {steps.length > 0 && <ProgressLog steps={steps} />}
      {results.length > 0 && (
        <>
          <div className="results-grid">
            {pageResults.map((r, i) => (
              <ResourceCard key={i} resource={r} />
            ))}
          </div>
          <Pagination
            page={page}
            total={results.length}
            onPage={setPage}
          />
        </>
      )}
    </div>
  );
}

export default App;
