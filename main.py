import os
from connectors.openaire import OpenAIREConnector
from connectors.skgif import SKGIFConnector
from vector_store import VectorStoreManager

def main():
    print("=== TESTING CONNECTOR AND VECTOR STORE INTEGRATION (RAG) ===\n")

    # 1. Initialize Vector Store
    vsm = VectorStoreManager()

    # 2. Fetch records from SKG-IF (JSON-LD) API
    print("--> Fetching data from SKG-IF API...")
    skgif_conn = SKGIFConnector("https://cris.uns.ac.rs/api/skg-if/product")
    skgif_records = skgif_conn.fetch_records(limit=500)

    # 3. Fetch records from OpenAIRE CERIF (XML) API
    print("\n--> Fetching data from OpenAIRE API...")
    openaire_conn = OpenAIREConnector(
        "https://cris.uns.ac.rs/api/export/OAIHandlerOpenAIRECRIS?verb=ListRecords&set=openaire_cris_publications&metadataPrefix=oai_cerif_openaire"
    )
    openaire_records = openaire_conn.fetch_records(limit=500)

    # 4. Combine all collected records
    all_records = skgif_records + openaire_records
    print(f"\n--> Total records ready for indexing: {len(all_records)}")

    # 5. Store in ChromaDB
    if all_records:
        vsm.add_records(all_records)
    else:
        print("--> Warning: No records found to index.")

if __name__ == "__main__":
    main()