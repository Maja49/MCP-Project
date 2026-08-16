import os
import sys

# Postavljanje radnog direktorijuma na koren projekta
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from vector_store import VectorStoreManager

# Inicijalizacija FastMCP servera
mcp = FastMCP("TeslaRIS MCP Server")

#  putanja do ChromaDB
db_path = os.path.join(PROJECT_ROOT, "chroma_db")
vsm = VectorStoreManager(db_path=db_path)

@mcp.tool()
def search_tesla_ris_publications(query: str, top_k: int = 5, source: str = "all") -> str:
    """
    Search publications, research papers, and journals from TeslaRIS CRIS/RIMS platform using semantic RAG.
    
    Args:
        query: Search query or topic in English or Serbian (e.g. 'veštačka inteligencija', 'machine learning').
        top_k: Number of search results to return (default is 5, max 20).
        source: Filter by metadata source format: 'all', 'xml' (OpenAIRE CERIF), or 'json' (SKG-IF).
    """
    filter_source = None if source == "all" else source
    results = vsm.search(query=query, top_k=top_k, source=filter_source)
    
    if not results:
        return "No matching records found in TeslaRIS database."
        
    formatted_output = []
    for item in results:
        authors_str = ", ".join(item.get("authors", [])) if item.get("authors") else "Unknown author"
        entry = (
            f"Type: {item.get('entity_type', 'article').upper()}\n"
            f"Title: {item.get('title')}\n"
            f"Authors: {authors_str}\n"
            f"Source: {item.get('source')}\n"
            f"Abstract: {item.get('abstract')}\n"
            f"----------------------------------------"
        )
        formatted_output.append(entry)
        
    return "\n\n".join(formatted_output)

if __name__ == "__main__":
    mcp.run(transport="stdio")