import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from vector_store import VectorStoreManager

app = FastAPI(
    title="TeslaRIS RAG & MCP API",
    description="API for semantic search over TeslaRIS publications and journals with MCP support.",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vsm = VectorStoreManager()

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "TeslaRIS RAG & MCP Explorer API is running.",
        "indexed_records": vsm.get_count()
    }

@app.get("/api/stats")
def get_stats():
    return {
        "total_records": vsm.get_count(),
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "mcp_status": "Ready"
    }

@app.get("/api/search")
def search(
    query: str = Query(..., description="Search query string"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to return"),
    entity_type: Optional[str] = Query("all", description="Filter by entity type: 'all', 'article', or 'journal'")
):
    """
    Semantic search endpoint supporting entity filtering.
    """
    filter_type = None if entity_type == "all" else entity_type
    results = vsm.search(query=query, top_k=top_k, entity_type=filter_type)
    
    return {
        "query": query,
        "entity_type_filter": entity_type,
        "total_results": len(results),
        "results": results
    }

# Ova sekcija drži server pokrenutim!
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)