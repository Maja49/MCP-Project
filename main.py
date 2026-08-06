from connectors.openaire import OpenAIREConnector
from connectors.skgif import SKGIFConnector
from vector_store import VectorStoreManager

def main():
    print("=== TESTING CONNECTOR AND VECTOR STORE INTEGRATION (RAG) ===\n")

    # 1. Fetching data from SKG-IF (100 records)
    skgif_url = "https://cris.uns.ac.rs/api/skg-if/product?page=0&page_size=100"
    skgif_conn = SKGIFConnector(endpoint_url=skgif_url)
    print("--> Fetching data from SKG-IF API...")
    skgif_data = skgif_conn.fetch_records(limit=100)
    print(f"    [SKG-IF] Successfully retrieved {len(skgif_data)} records.\n")

    # 2. Fetching data from OpenAIRE (100 records)
    openaire_url = "https://cris.uns.ac.rs/api/export/OAIHandlerOpenAIRECRIS?verb=ListRecords&set=openaire_cris_publications&metadataPrefix=oai_cerif_openaire"
    openaire_conn = OpenAIREConnector(endpoint_url=openaire_url)
    print("--> Fetching data from OpenAIRE API...")
    openaire_data = openaire_conn.fetch_records(limit=100)
    print(f"    [OpenAIRE] Successfully retrieved {len(openaire_data)} records.\n")

    # 3. Combining all fetched records into a single list
    all_publications = skgif_data + openaire_data
    print(f"--> Total records ready for indexing: {len(all_publications)}")

    # 4. Initializing and populating the vector store
    vector_store = VectorStoreManager()
    vector_store.add_records(all_publications)

    print("\n" + "="*50 + "\n")

    # 5. Testing Semantic / RAG Search
    query = "pšenica i brašno"  # Searching for publications related to wheat/flour
    search_results = vector_store.search(query=query, n_results=5)

    print(f"\n[RAG Search Results for '{query}']:")
    for idx, record in enumerate(search_results, 1):
        print(f"\n{idx}. Title: {record['title']}")
        print(f"   Source: {record['source']}")
        print(f"   Authors / Author IDs: {record['authors']}")

if __name__ == "__main__":
    main()