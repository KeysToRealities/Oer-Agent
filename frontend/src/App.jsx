import { useState } from "react";
import SearchBar from "./components/SearchBar";
import ProgressLog from "./components/ProgressLog";
import ResourceCard from "./components/ResourceCard";
import "./App.css";

function App() {
  const [steps, setSteps] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  function handleSearch(course) {
    setSteps([]);
    setResults([]);
    setLoading(true);

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

  return (
    <div className="app">
      <h1>OER Agent</h1>
      <p className="subtitle">Find open educational resources for your course</p>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {steps.length > 0 && <ProgressLog steps={steps} />}
      {results.length > 0 && (
        <div className="results">
          {results.map((r, i) => (
            <ResourceCard key={i} resource={r} />
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
