import requests
from xml.etree import ElementTree as ET
from typing import List, Dict, Any
from .base import BaseConnector

class OpenAIREConnector(BaseConnector):
    """
    Konektor za OpenAIRE CERIF (XML) API TeslaRIS platforme.
    """
    def fetch_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        print(f"--> [OpenAIRE] Preuzimam podatke sa: {self.endpoint_url}")
        
        response = requests.get(self.endpoint_url)
        if response.status_code != 200:
            raise Exception(f"OpenAIRE Greška: HTTP status {response.status_code}")

        root = ET.fromstring(response.content)
        records = []
        xml_records = root.findall('.//{*}record')

        for record in xml_records[:limit]:
            titles = record.findall('.//{*}Title') or record.findall('.//{*}cfTitle')
            title_text = titles[0].text.strip() if titles and titles[0].text else "Naslov nedostupan"

            header_id = record.find('.//{*}identifier')
            rec_id = header_id.text if header_id is not None else "N/A"

            records.append({
                "id": rec_id,
                "title": title_text,
                "abstract": "CERIF Metadata Publication Record",
                "authors": ["TeslaRIS Istraživač"],
                "source": "TeslaRIS OpenAIRE (XML)"
            })

        return records