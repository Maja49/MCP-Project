import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

class VectorStoreManager:
    """
    Klasa zadužena za upravljanje ChromaDB vektorskom bazom,
    indeksiranje radova i semantičku pretragu za RAG.
    """
    def __init__(self, db_path: str = "./chroma_db"):
        # Inicijalizacija lokalne baze na disku
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Podrazumevani model za pretvaranje teksta u vektore
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Kreiranje ili preuzimanje kolekcije naučnih radova
        self.collection = self.client.get_or_create_collection(
            name="teslaris_publications",
            embedding_function=self.embedding_fn
        )

    def add_records(self, records: List[Dict[str, Any]]):
        """
        Gura preuzete radove iz konektora u vektorsku bazu.
        """
        documents = []
        metadatas = []
        ids = []

        for record in records:
            # Sastavljamo tekst za vektorsku pretragu (naslov + apstrakt)
            text_content = f"Title: {record['title']}. Abstract: {record.get('abstract', '')}"
            
            documents.append(text_content)
            metadatas.append({
                "title": record["title"],
                "source": record["source"],
                "authors": ", ".join(record.get("authors", []))
            })
            ids.append(str(record["id"]))

        if ids:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"--> [VectorStore] Uspešno indeksirano {len(ids)} radova u bazu!")

    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Semantička (RAG) pretraga radova na osnovu upita.
        """
        print(f"--> [VectorStore] Pretražujem bazu za upit: '{query}'")
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        formatted_results = []
        if results and results['metadatas']:
            for i in range(len(results['metadatas'][0])):
                meta = results['metadatas'][0][i]
                doc = results['documents'][0][i]
                dist = results['distances'][0][i] if 'distances' in results else None
                
                formatted_results.append({
                    "title": meta['title'],
                    "authors": meta['authors'],
                    "source": meta['source'],
                    "content": doc,
                    "distance": dist
                })

        return formatted_results