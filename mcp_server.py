import sys
from fastmcp import FastMCP
from vector_store import VectorStoreManager

# 1. Inicijalizacija MCP Servera
mcp = FastMCP("TeslaRIS-RAG-Server")

# 2. Inicijalizacija vektorske baze
vector_store = VectorStoreManager()


@mcp.tool()
def search_tesla_ris_publications(query: str, n_results: int = 5) -> str:
    """
    Pretražuje naučne publikacije i istraživačke radove sa TeslaRIS platforme 
    (Univerzitet u Novom Sadu / CRIS UNS).

    Koristi se kada korisnik pita o istraživačkim radovima, temama, autorima ili 
    naučnim dostignućima na Univerzitetu.

    Args:
        query: Upit na prirodnom jeziku (npr. 'pšenica i brašno', 'veštačka inteligencija u medicini')
        n_results: Broj relevantnih radova koje treba vratiti (podrazumevano 5)

    Returns:
        Tekstualni format pronađenih radova sa naslovom, izvorom i autorima.
    """
    # Za logovanje uvek koristimo sys.stderr umesto print()
    sys.stderr.write(f"--> [MCP Server] Pozvan alat za upit: '{query}'\n")

    results = vector_store.search(query=query, n_results=n_results)

    if not results:
        return "Nije pronađen nijedan relevantan rad za navedeni upit."

    formatted_output = []
    for idx, item in enumerate(results, 1):
        title = item.get("title", "Naslov nepoznat")
        source = item.get("source", "Izvor nepoznat")
        authors = item.get("authors", [])

        if isinstance(authors, list):
            authors_str = ", ".join(authors)
        else:
            authors_str = str(authors)

        formatted_output.append(
            f"Rad #{idx}:\n"
            f"- Naslov: {title}\n"
            f"- Izvor: {source}\n"
            f"- Autori: {authors_str}\n"
        )

    return "\n".join(formatted_output)


if __name__ == "__main__":
    # Pokrećemo server preko STDIO transporta bez print poruka na STDOUT
    mcp.run(transport="stdio")