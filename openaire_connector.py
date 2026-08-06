import requests
from xml.etree import ElementTree as ET
from typing import List, Dict, Any

class OpenAIREConnector:
    """
    Konektor za preuzimanje i parsiranje naučnih publikacija sa TeslaRIS 
    platforme u skladu sa OpenAIRE CERIF XML standardom, sa podrškom za 
    OAI-PMH paginaciju preko 'resumptionToken'-a.
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    def fetch_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        records = []
        current_url = self.endpoint_url
        base_url = self.endpoint_url.split('?')[0]

        print(f"--> [OpenAIRE] Započinjem preuzimanje (cilj: {limit} radova)...")

        while len(records) < limit and current_url:
            print(f"--> Povezujem se na OpenAIRE URL: {current_url}")
            response = requests.get(current_url)
            
            if response.status_code != 200:
                raise Exception(f"Greška prilikom preuzimanja podataka: HTTP status {response.status_code}")
                
            root = ET.fromstring(response.content)
            page_records = self._parse_xml_records(root)
            
            # Dodajemo samo onoliko radova koliko nedostaje do limita
            needed = limit - len(records)
            records.extend(page_records[:needed])
            
            print(f"    [Paginacija] Preuzeto u ovoj turi: {len(page_records)} | Ukupno sakupljeno: {len(records)}/{limit}")

            if len(records) >= limit:
                break

            # Tražimo resumptionToken za učitavanje sledeće stranice
            token_elem = root.find('.//{*}resumptionToken')
            if token_elem is not None and token_elem.text and token_elem.text.strip():
                token = token_elem.text.strip()
                # OAI-PMH standard zahteva samo verb=ListRecords i resumptionToken
                current_url = f"{base_url}?verb=ListRecords&resumptionToken={token}"
            else:
                # Nema više stranica za preuzimanje
                current_url = None

        return records

    def _parse_xml_records(self, root: ET.Element) -> List[Dict[str, Any]]:
        records = []
        xml_records = root.findall('.//{*}record')
        
        for record in xml_records:
            metadata = record.find('.//{*}metadata')
            if metadata is None:
                continue

            # Tražimo naslove (CERIF koristi cfTitle ili Title)
            titles = record.findall('.//{*}Title') or record.findall('.//{*}cfTitle')
            abstracts = record.findall('.//{*}Abstract') or record.findall('.//{*}cfAbstr')
            
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

            # Sakupljanje autora (Firstname, Familyname ili Person / cfPers)
            first_names = [e.text.strip() for e in record.findall('.//{*}Firstname') if e.text]
            family_names = [e.text.strip() for e in record.findall('.//{*}Familyname') if e.text]
            
            author_names = []
            for fn, ln in zip(first_names, family_names):
                author_names.append(f"{fn} {ln}")

            if not author_names:
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