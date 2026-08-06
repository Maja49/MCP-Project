import requests
from xml.etree import ElementTree as ET
from typing import List, Dict, Any

class OpenAIREConnector:
    """
    Konektor za preuzimanje i parsiranje naučnih publikacija sa TeslaRIS 
    platforme u skladu sa OpenAIRE CERIF XML standardom.
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    def fetch_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        print(f"--> Povezujem se na TeslaRIS API: {self.endpoint_url}")
        response = requests.get(self.endpoint_url)
        
        print(f"--> Status odgovora: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Greška prilikom preuzimanja podataka: HTTP status {response.status_code}")
            
        print("--> Započinjem parsiranje XML-a...")
        return self._parse_xml(response.content, limit)

    def _parse_xml(self, xml_content: bytes, limit: int) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_content)
        records = []
        
        # Pronalaženje svih record zapisa bez obzira na tačan namespace
        xml_records = root.findall('.//{*}record')
        print(f"--> Pronađeno ukupno XML zapisa: {len(xml_records)}")
        
        for record in xml_records[:limit]:
            metadata = record.find('.//{*}metadata')
            if metadata is None:
                continue

            # Tražimo naslove (CERIF koristi cfTitle ili Title)
            titles = record.findall('.//{*}Title') or record.findall('.//{*}cfTitle')
            abstracts = record.findall('.//{*}Abstract') or record.findall('.//{*}cfAbstr')
            
            # Tražimo sve tekstualne čvorove ili imena
            title_text = "Naslov nedostupan"
            if titles:
                for t in titles:
                    if t.text and len(t.text.strip()) > 0:
                        title_text = t.text.strip()
                        break

            abstract_text = "Apstrakt nedostupan"
            if abstracts:
                for a in abstracts:
                    if a.text and len(a.text.strip()) > 0:
                        abstract_text = a.text.strip()
                        break

            # Sakupljanje autora (Person, cfPers, Firstname, Familyname)
            first_names = [e.text.strip() for e in record.findall('.//{*}Firstname') if e.text]
            family_names = [e.text.strip() for e in record.findall('.//{*}Familyname') if e.text]
            
            author_names = []
            for fn, ln in zip(first_names, family_names):
                author_names.append(f"{fn} {ln}")

            if not author_names:
                # Proba alternativnih tagova za imena
                authors_raw = record.findall('.//{*}Person') or record.findall('.//{*}cfPers')
                for a in authors_raw:
                    if a.text and len(a.text.strip()) > 0:
                        author_names.append(a.text.strip())

            records.append({
                "title": title_text,
                "abstract": abstract_text,
                "authors": author_names if author_names else ["Nepoznat autor"],
                "source": "TeslaRIS OpenAIRE CERIF"
            })
            
        return records

if __name__ == "__main__":
    print("=== Pokretanje OpenAIRE konektora ===")
    TEST_URL = "https://cris.uns.ac.rs/api/export/OAIHandlerOpenAIRECRIS?verb=ListRecords&set=openaire_cris_publications&metadataPrefix=oai_cerif_openaire"
    
    connector = OpenAIREConnector(endpoint_url=TEST_URL)
    try:
        data = connector.fetch_records(limit=5)
        print(f"\nUspešno preuzeto i parsirano {len(data)} radova!\n")
        for i, item in enumerate(data, 1):
            print(f"--- Rad {i} ---")
            print(f"Naslov: {item['title']}")
            print(f"Autori: {', '.join(item['authors'])}")
            print(f"Apstrakt: {item['abstract'][:150]}...\n")
    except Exception as e:
        print(f"Došlo je do greške: {e}")