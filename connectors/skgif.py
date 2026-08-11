import requests
from typing import List, Dict, Any
from .base import BaseConnector

class SKGIFConnector(BaseConnector):
    """
    Connector for SKG-IF (JSON-LD) API of the TeslaRIS platform with pagination support.
    """
    def fetch_records(self, limit: int = 500) -> List[Dict[str, Any]]:
        print(f"--> [SKG-IF] Fetching data from API (target: {limit} records)...")
        records = []
        page = 0
        page_size = 100
        base_url = self.endpoint_url.split('?')[0]

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
                titles = item.get("titles", {})
                title_text = titles.get("en", [None])[0] if isinstance(titles.get("en"), list) else titles.get("en")
                if not title_text:
                    title_text = next(iter(titles.values()), ["Title unavailable"])[0] if titles else "Title unavailable"

                contributions = item.get("contributions", [])
                authors = [contrib.get("by", "Unknown ID") for contrib in contributions if contrib.get("role") == "author"]

                raw_id = item.get("@id", "")
                clean_id = raw_id.split("/")[-1] if "/" in raw_id else item.get("local_identifier", "N/A")

                records.append({
                    "id": clean_id,
                    "title": title_text,
                    "abstract": "Description available in connected graph.",
                    "authors": authors if authors else ["Unknown author"],
                    "source": "TeslaRIS SKG-IF (JSON)",
                    "entity_type": "article"
                })

                if len(records) >= limit:
                    break

            page += 1

        print(f"    [SKG-IF] Successfully retrieved {len(records)} records.")
        return records