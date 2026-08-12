import requests
from typing import List, Dict, Any
from .base import BaseConnector

class SKGIFConnector(BaseConnector):
    """
    Connector for SKG-IF (JSON-LD) API of the TeslaRIS platform with pagination support.
    """
    def fetch_records(self, limit: int = 500) -> List[Dict[str, Any]]:
        print(f"--> [SKG-IF JSON] Fetching data from API (target: {limit} records)...")
        records = []
        page = 0
        page_size = 100
        base_url = self.endpoint_url.split('?')[0]

        journal_keywords = ["journal", "transactions", "review", "bulletin", "annals"]

        while len(records) < limit:
            url = f"{base_url}?page={page}&page_size={page_size}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"--> [SKG-IF] Warning: Received status code {response.status_code}. Stopping pagination.")
                break
                
            data = response.json()
            graph = data.get("@graph", [])
            
            if not graph:
                break

            for item in graph:
                # 1. Naslov
                titles = item.get("titles", {})
                title_text = titles.get("en", [None])[0] if isinstance(titles.get("en"), list) else titles.get("en")
                if not title_text:
                    title_text = next(iter(titles.values()), ["Title unavailable"])[0] if titles else "Title unavailable"

                # 2. Autori
                contributions = item.get("contributions", [])
                authors = [contrib.get("by", "Unknown ID") for contrib in contributions if contrib.get("role") == "author"]

                # 3. Čišćenje ID-ja (uzima numerički/krajnji deo ID-ja)
                raw_id = item.get("@id", "")
                clean_id = raw_id.split("/")[-1] if "/" in raw_id else item.get("local_identifier", "N/A")

                # 4. Detekcija tipa entiteta (Journal vs Article)
                raw_type = str(item.get("@type") or item.get("type") or "").lower()
                title_lower = title_text.lower()

                if "journal" in raw_type or "periodical" in raw_type or (any(kw in title_lower for kw in journal_keywords) and len(title_text.split()) < 8):
                    entity_type = "journal"
                    abstract_text = "Profil naučnog časopisa (SKG-IF)"
                else:
                    entity_type = "article"
                    abstract_text = "Opis dostupan u povezanom grafu publikacija."

                records.append({
                    "id": clean_id,
                    "title": title_text,
                    "abstract": abstract_text,
                    "authors": authors if authors else ["Nepoznati autor"],
                    "source": "SKG-IF (JSON)",
                    "entity_type": entity_type
                })

                if len(records) >= limit:
                    break

            page += 1

        print(f"    [SKG-IF JSON] Successfully retrieved {len(records)} records.")
        return records