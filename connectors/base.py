from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseConnector(ABC):
    """
    
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    @abstractmethod
    def fetch_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        
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