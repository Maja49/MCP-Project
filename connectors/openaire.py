import requests
from xml.etree import ElementTree as ET
from typing import List, Dict, Any
from .base import BaseConnector

class OpenAIREConnector(BaseConnector):
    """
    Konektor za OpenAIRE CERIF (XML) API TeslaRIS platforme sa podrškom 
    za OAI-PMH paginaciju preko 'resumptionToken'-a.
    """
    def fetch_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        records = []
        current_url = self.endpoint_url
        base_url = self.endpoint_url.split('?')[0]

        print(f"--> [OpenAIRE] Preuzimam podatke sa: {self.endpoint_url}")

        while len(records) < limit and current_url:
            response = requests.get(current_url)
            if response.status_code != 200:
                raise Exception(f"OpenAIRE Greška: HTTP status {response.status_code}")

            root = ET.fromstring(response.content)
            page_records = self._parse_xml_records(root)

            needed = limit - len(records)
            records.extend(page_records[:needed])

            if len(records) >= limit:
                break

            # Tražimo resumptionToken za sledeću stranicu
            token_elem = root.find('.//{*}resumptionToken')
            if token_elem is not None and token_elem.text and token_elem.text.strip():
                token = token_elem.text.strip()
                current_url = f"{base_url}?verb=ListRecords&resumptionToken={token}"
            else:
                current_url = None

        return records

    def _parse_xml_records(self, root: ET.Element) -> List[Dict[str, Any]]:
        records = []
        xml_records = root.findall('.//{*}record')

        for record in xml_records:
            metadata = record.find('.//{*}metadata')
            if metadata is None:
                continue

            # Parsiranje naslova
            titles = record.findall('.//{*}Title') or record.findall('.//{*}cfTitle')
            title_text = "Naslov nedostupan"
            if titles:
                for t in titles:
                    if t.text and len(t.text.strip()) > 0:
                        title_text = t.text.strip()
                        break

            # Parsiranje apstrakta
            abstracts = record.findall('.//{*}Abstract') or record.findall('.//{*}cfAbstr')
            abstract_text = "Apstrakt nedostupan"
            if abstracts:
                for a in abstracts:
                    if a.text and len(a.text.strip()) > 0:
                        abstract_text = a.text.strip()
                        break

            # Parsiranje autora
            first_names = [e.text.strip() for e in record.findall('.//{*}Firstname') if e.text]
            family_names = [e.text.strip() for e in record.findall('.//{*}Familyname') if e.text]
            author_names = [f"{fn} {ln}" for fn, ln in zip(first_names, family_names)]

            if not author_names:
                authors_raw = record.findall('.//{*}Person') or record.findall('.//{*}cfPers')
                for a in authors_raw:
                    if a.text and len(a.text.strip()) > 0:
                        author_names.append(a.text.strip())

            # ID rada
            header_id = record.find('.//{*}identifier')
            rec_id = header_id.text if header_id is not None else "N/A"

            records.append({
                "id": rec_id,
                "title": title_text,
                "abstract": abstract_text,
                "authors": author_names if author_names else ["Nepoznat autor"],
                "source": "TeslaRIS OpenAIRE (XML)"
            })

        return records