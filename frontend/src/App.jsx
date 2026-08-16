import React, { useState, useEffect } from 'react';
import { Search, ExternalLink, Database, Cpu, CheckCircle2, Layers } from 'lucide-react';

function App() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [sourceFilter, setSourceFilter] = useState('all'); // Filter za izvor (all / xml / json)
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total_records: 0, embedding_model: '', mcp_status: '' });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Error fetching stats:", err);
    }
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      // (xml/json/all)
      const res = await fetch(
        `http://localhost:8000/api/search?query=${encodeURIComponent(query)}&top_k=${topK}&source=${sourceFilter}`
      );
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error("Error searching:", err);
    } finally {
      setLoading(false);
    }
  };

  // Dinamičko usmeravanje na TeslaRIS
  const getTargetUrl = (item) => {
    if (!item) return "https://cris.uns.ac.rs";

    const numericId = item.id ? String(item.id).replace(/[^0-9]/g, "") : "";

    // 1. Ako je casopis -> ide na pretragu po nazivu časopisa
    if (item.entity_type === "journal") {
      const encodedTitle = encodeURIComponent(item.title || "");
      return `https://cris.uns.ac.rs/sr/advanced-search?searchQuery=${encodedTitle}&tab=publications&search=simple`;
    }

    // 2. Ako je rad/clanak -> ide direktno na publikaciju preko ID-ja
    if (numericId) {
      return `https://cris.uns.ac.rs/sr/scientific-results/journal-publication/${numericId}`;
    }

    return "https://cris.uns.ac.rs";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <header className="flex items-center justify-between border-b border-slate-800 pb-5">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
              <Cpu className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                TeslaRIS RAG & MCP Explorer
              </h1>
              <p className="text-xs text-slate-400">Master Thesis Project • CRIS/RIMS AI Integration</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>FastAPI & ChromaDB Active</span>
          </div>
        </header>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Indexed Records</p>
              <h3 className="text-2xl font-bold text-white mt-1">{stats.total_records}</h3>
              <p className="text-xs text-indigo-400 mt-0.5">OpenAIRE (XML) + SKG-IF (JSON)</p>
            </div>
            <Database className="w-8 h-8 text-indigo-500/40" />
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Embedding Model</p>
              <h3 className="text-sm font-semibold text-white mt-1 truncate max-w-[200px]">{stats.embedding_model || 'MiniLM-L12-v2'}</h3>
              <p className="text-xs text-cyan-400 mt-0.5">Multilingual (Serbian & English)</p>
            </div>
            <Cpu className="w-8 h-8 text-cyan-500/40" />
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">MCP Protocol Status</p>
              <div className="flex items-center space-x-1.5 text-emerald-400 text-sm font-semibold mt-1">
                <CheckCircle2 className="w-4 h-4" />
                <span>Ready for AI Agents</span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Tool: search_tesla_ris_publications</p>
            </div>
          </div>
        </div>

        {/* Search Box */}
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-xl">
          <form onSubmit={handleSearch} className="space-y-4">
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Ask or Search Query (Semantic Match)
            </label>
            
            <div className="flex flex-col md:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-500" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Unesite pojam za pretragu (npr. komunikacija, elektrodem, AI...)"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              {/* Filter po izvoru */}
              <div className="flex items-center space-x-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2">
                <Layers className="w-4 h-4 text-slate-400" />
                <select
                  value={sourceFilter}
                  onChange={(e) => setSourceFilter(e.target.value)}
                  className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
                >
                  <option value="all" className="bg-slate-900">All Sources</option>
                  <option value="xml" className="bg-slate-900">OpenAIRE (XML)</option>
                  <option value="json" className="bg-slate-900">SKG-IF (JSON)</option>
                </select>
              </div>

              {/* Top K Selector */}
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-3 text-xs text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
                <option value={15}>Top 15</option>
              </select>

              <button
                type="submit"
                disabled={loading}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-white font-medium px-6 py-3 rounded-xl transition-all text-sm flex items-center justify-center shadow-lg shadow-indigo-600/20"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Search Results ({results.length})</span>
          </h2>

          <div className="space-y-3">
            {results.map((item, index) => (
              <div 
                key={index} 
                className="bg-slate-900/50 border border-slate-800/80 hover:border-slate-700 p-5 rounded-xl transition-all flex justify-between items-start group"
              >
                <div className="space-y-2 max-w-4xl">
                  <div className="flex items-center space-x-2">
                    {/*  */}
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-indigo-400 border border-slate-700">
                      {item.source}
                    </span>
                    {/*  (Article ili Journal) */}
                    <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
                      item.entity_type === 'journal' 
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' 
                        : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    }`}>
                      {item.entity_type === 'journal' ? 'Journal' : 'Article'}
                    </span>
                    {item.similarity_score && (
                      <span className="text-[10px] text-slate-500">
                        Score: {item.similarity_score}
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors">
                    {item.title}
                  </h3>

                  <p className="text-xs text-slate-400 line-clamp-2">
                    {item.abstract}
                  </p>

                  <div className="text-xs text-slate-500">
                    <span className="font-medium text-slate-400">Authors / Info: </span>
                    {Array.isArray(item.authors) ? item.authors.join(', ') : (item.authors || 'Unknown')}
                  </div>
                </div>

                {/* Preusmeravanje na TeslaRIS */}
                <a
                  href={getTargetUrl(item)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2.5 text-slate-500 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition-all"
                  title={item.entity_type === 'journal' ? "Search journal on TeslaRIS" : "Open article on TeslaRIS"}
                >
                  <ExternalLink className="w-5 h-5" />
                </a>
              </div>
            ))}

            {!loading && results.length === 0 && (
              <div className="text-center py-12 bg-slate-900/20 border border-dashed border-slate-800 rounded-xl text-slate-500 text-sm">
                No results found. Try a different search term.
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;