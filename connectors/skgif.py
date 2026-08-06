import requests
from typing import List, Dict, Any
from .base import BaseConnector

class SKGIFConnector(BaseConnector):
    """
    Konektor za SKG-IF (JSON-LD) API TeslaRIS platforme.
    """
    def fetch_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        print(f"--> [SKG-IF] Preuzimam podatke sa: {self.endpoint_url}")
        
        response = requests.get(self.endpoint_url)
        if response.status_code != 200:
            raise Exception(f"SKG-IF Greška: HTTP status {response.status_code}")
            
        data = response.json()
        graph = data.get("@graph", [])
        records = []

        for item in graph[:limit]:
            # Izdvajanje naslova
            titles = item.get("titles", {})
            title_text = titles.get("en", [None])[0] if isinstance(titles.get("en"), list) else titles.get("en")
            if not title_text:
                title_text = next(iter(titles.values()), ["Naslov nedostupan"])[0] if titles else "Naslov nedostupan"

            # Izdvajanje autora (ID-jevi)
            contributions = item.get("contributions", [])
            authors = [contrib.get("by", "Nepoznat ID") for contrib in contributions if contrib.get("role") == "author"]

            records.append({
                "id": item.get("local_identifier", "N/A"),
                "title": title_text,
                "abstract": "Opis dostupan u povezanom grafu.", # SKG-IF vodi opis u odvojenim resursima
                "authors": authors if authors else ["Nepoznat autor"],
                "source": "TeslaRIS SKG-IF (JSON)"
            })

        return records