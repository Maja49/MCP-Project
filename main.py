from connectors.openaire import OpenAIREConnector
from connectors.skgif import SKGIFConnector

def main():
    print("=== TESTIRANJE MODULARNE ARHITEKTURA KONEKTORA ===\n")

    # 1. Testiramo OpenAIRE Konektor (XML)
    openaire_url = "https://cris.uns.ac.rs/api/export/OAIHandlerOpenAIRECRIS?verb=ListRecords&set=openaire_cris_publications&metadataPrefix=oai_cerif_openaire"
    openaire_conn = OpenAIREConnector(endpoint_url=openaire_url)
    openaire_data = openaire_conn.fetch_records(limit=3)

    print(f"\n[OpenAIRE] Preuzeto {len(openaire_data)} zapisa:")
    for r in openaire_data:
        print(f" - [{r['source']}] {r['title']}")

    print("\n" + "="*50 + "\n")

    # 2. Testiramo SKG-IF Konektor (JSON)
    skgif_url = "https://cris.uns.ac.rs/api/skg-if/product?page=0&page_size=50"
    skgif_conn = SKGIFConnector(endpoint_url=skgif_url)
    skgif_data = skgif_conn.fetch_records(limit=3)

    print(f"\n[SKG-IF] Preuzeto {len(skgif_data)} zapisa:")
    for r in skgif_data:
        print(f" - [{r['source']}] {r['title']}")

if __name__ == "__main__":
    main()