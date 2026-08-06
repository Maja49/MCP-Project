from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseConnector(ABC):
    """
    Apstraktna bazna klasa za sve konektore naučnoistraživačkih baza.
    Omogućava da MCP server komunicira sa bilo kojim izvorom podataka 
    koristeći identičan interfejs.
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    @abstractmethod
    def fetch_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Metoda koja preuzima podatke sa API-ja i vraća ih u standardizovanom formatu:
        [
            {
                "id": str,
                "title": str,
                "abstract": str,
                "authors": List[str],
                "source": str
            }
        ]
        """
        pass