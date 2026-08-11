import requests
from xml.etree import ElementTree as ET
from typing import List, Dict, Any
from .base import BaseConnector

class OpenAIREConnector(BaseConnector):
    """
    Connector for OpenAIRE CERIF (XML) API of the TeslaRIS platform.
    """
    def fetch_records(self, limit: int = 500) -> List[Dict[str, Any]]:
        records = []
        current_url = self.endpoint_url
        base_url = self.endpoint_url.split('?')[0]

        print(f"--> [OpenAIRE] Fetching data from: {self.endpoint_url}")

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

        # Proširene ključne reči koje ukazuju na časopis/serijsku publikaciju
        journal_keywords = [
            "journal", "transactions", "communications", 
            "review", "bulletin", "proceedings", "annals", "letters"
        ]

        for record in xml_records:
            header = record.find('./{*}header')
            if header is not None and header.attrib.get('status') == 'deleted':
                continue

            metadata = record.find('.//{*}metadata')
            if metadata is None:
                continue

            raw_id = ""
            if header is not None:
                header_id_elem = header.find('./{*}identifier')
                if header_id_elem is not None and header_id_elem.text:
                    raw_id = header_id_elem.text.strip()

            clean_id = raw_id.split(":")[-1] if ":" in raw_id else raw_id
            clean_id = clean_id.split("/")[-1] if "/" in clean_id else clean_id

            pub_elem = metadata.find('.//{*}cfResPubl') or metadata
            titles = pub_elem.findall('./{*}cfTitle') or pub_elem.findall('.//{*}Title') or pub_elem.findall('.//{*}title')
            
            title_text = ""
            for t in titles:
                if t.text and len(t.text.strip()) > 0:
                    title_text = t.text.strip()
                    break

            if not title_text:
                continue

            # Određivanje da li je časopis ili konkretan rad
            lower_title = title_text.lower()
            abstracts = pub_elem.findall('./{*}cfAbstr') or pub_elem.findall('.//{*}Abstract') or pub_elem.findall('.//{*}description')
            
            # Poboljšana heuristika za klasifikaciju
            is_journal = any(kw in lower_title for kw in journal_keywords) and not abstracts and len(title_text.split()) < 10

            if is_journal:
                entity_type = "journal"
                abstract_text = "Journal Profile / Periodical Publication"
            else:
                entity_type = "article"
                abstract_text = "Abstract unavailable"
                for a in abstracts:
                    if a.text and len(a.text.strip()) > 0:
                        abstract_text = a.text.strip()
                        break

            # Autori
            author_names = []
            first_names = [e.text.strip() for e in (pub_elem.findall('.//{*}Firstname') + pub_elem.findall('.//{*}cfFirstNames')) if e.text and e.text.strip()]
            family_names = [e.text.strip() for e in (pub_elem.findall('.//{*}Familyname') + pub_elem.findall('.//{*}cfFamilyNames')) if e.text and e.text.strip()]

            if first_names and family_names:
                for fn, ln in zip(first_names, family_names):
                    author_names.append(f"{fn} {ln}")

            if not author_names:
                creators = pub_elem.findall('.//{*}creator') or pub_elem.findall('.//{*}Person') or pub_elem.findall('.//{*}cfPers')
                for c in creators:
                    if c.text and len(c.text.strip()) > 0:
                        author_names.append(c.text.strip())

            records.append({
                "id": clean_id if clean_id else "N/A",
                "title": title_text,
                "abstract": abstract_text,
                "authors": author_names if author_names else ["Unknown author"],
                "source": "TeslaRIS OpenAIRE (XML)",
                "entity_type": entity_type
            })

        return records