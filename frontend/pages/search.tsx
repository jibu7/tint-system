import React, { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SearchPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults([]);
    try {
      const res = await fetch(`${API_BASE_URL}/api/formulation/${encodeURIComponent(searchTerm)}`);
      if (!res.ok) throw new Error("No results found");
      const data = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Error searching");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSearch} className="flex gap-2 mb-4">
        <input
          type="text"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          placeholder="Enter color code"
          className="border px-3 py-2 rounded w-full"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      {error && <div className="text-red-600 mb-4">{error}</div>}
      {results.length > 0 && (
        <table className="w-full border">
          <thead>
            <tr>
              <th>Paint Type</th>
              <th>Base Paint</th>
              <th>Colorant Details</th>
              <th>Color (Hex)</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item: any, idx: number) => (
              <tr key={idx}>
                <td>{item.paint_type}</td>
                <td>{item.base_paint}</td>
                <td>
                  {item.colorant_details.map((c: any, i: number) => (
                    <div key={i}>
                      {c.colorant_name}: {c.weight_g}g / {c.volume_ml}ml
                    </div>
                  ))}
                </td>
                <td>
                  <span style={{ background: item.color_rgb.hex, padding: "0 10px" }}>{item.color_rgb.hex}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
