import requests
import re
from xml.etree import ElementTree as ET
from typing import List, Dict, Any
from .base import BaseConnector

class OpenAIREConnector(BaseConnector):
    """
    Konektor za OpenAIRE CERIF (XML) API sa TeslaRIS platforme.
    """
    def fetch_records(self, limit: int = 500) -> List[Dict[str, Any]]:
        records = []
        current_url = self.endpoint_url
        base_url = self.endpoint_url.split('?')[0]

        print(f"--> [OpenAIRE XML] Preuzimanje podataka sa: {self.endpoint_url}")

        while len(records) < limit and current_url:
            response = requests.get(current_url)
            if response.status_code != 200:
                raise Exception(f"OpenAIRE Error: HTTP status {response.status_code}")

            root = ET.fromstring(response.content)
            page_records = self._parse_xml_records(root)

            needed = limit - len(records)
            records.extend(page_records[:needed])

            if len(records) >= limit:
                break

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
            header = record.find('./{*}header')
            if header is not None and header.attrib.get('status') == 'deleted':
                continue

            metadata = record.find('.//{*}metadata')
            if metadata is None:
                continue

            # 1. Izvlačenje čisto brojčanog ID-ja
            raw_id = ""
            if header is not None:
                header_id_elem = header.find('./{*}identifier')
                if header_id_elem is not None and header_id_elem.text:
                    raw_id = header_id_elem.text.strip()

            numbers = re.findall(r'\d+', raw_id)
            clean_id = numbers[0] if numbers else raw_id

            pub_elem = metadata.find('.//{*}cfResPubl') or metadata.find('.//{*}Publication') or metadata
            
            # 2. Naslov
            titles = pub_elem.findall('./{*}cfTitle') or pub_elem.findall('.//{*}Title') or pub_elem.findall('.//{*}title')
            title_text = ""
            for t in titles:
                if t.text and len(t.text.strip()) > 0:
                    title_text = t.text.strip()
                    break

            if not title_text:
                continue

            # 3. Sažetak i Autori
            abstracts = pub_elem.findall('./{*}cfAbstr') or pub_elem.findall('.//{*}Abstract') or pub_elem.findall('.//{*}description')
            
            first_names = [e.text.strip() for e in (pub_elem.findall('.//{*}Firstname') + pub_elem.findall('.//{*}cfFirstNames')) if e.text and e.text.strip()]
            family_names = [e.text.strip() for e in (pub_elem.findall('.//{*}Familyname') + pub_elem.findall('.//{*}cfFamilyNames')) if e.text and e.text.strip()]

            author_names = []
            if first_names and family_names:
                for fn, ln in zip(first_names, family_names):
                    author_names.append(f"{fn} {ln}")

            if not author_names:
                creators = pub_elem.findall('.//{*}creator') or pub_elem.findall('.//{*}Person') or pub_elem.findall('.//{*}cfPers')
                for c in creators:
                    if c.text and len(c.text.strip()) > 0:
                        author_names.append(c.text.strip())

            # 4. Detekcija tipa entiteta (Journal vs Article)
            coar_type_elem = pub_elem.find('.//{*}Type')
            coar_type = coar_type_elem.text.strip() if coar_type_elem is not None and coar_type_elem.text else ""

            # Časopis je samo ako je striktno klasifikovan kao journal I nema navedene autore/sažetak rada
            is_journal = ("c_0640" in coar_type or "journal" in coar_type.lower()) and not author_names and not abstracts

            if is_journal:
                entity_type = "journal"
                abstract_text = "Profil naučnog časopisa / Periodična publikacija"
                issn_elem = pub_elem.find('.//{*}ISSN')
                if issn_elem is not None and issn_elem.text:
                    author_names = [f"ISSN: {issn_elem.text.strip()}"]
            else:
                entity_type = "article"
                abstract_text = "Sažetak nije dostupan"
                for a in abstracts:
                    if a.text and len(a.text.strip()) > 0:
                        abstract_text = a.text.strip()
                        break

            records.append({
                "id": clean_id if clean_id else "N/A",
                "title": title_text,
                "abstract": abstract_text,
                "authors": author_names if author_names else ["Nepoznati autor"],
                "source": "OpenAIRE (XML)",
                "entity_type": entity_type
            })

        return records