import os
import chromadb
from chromadb.config import Settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")


class VectorStoreManager:
    def __init__(self, db_path=DB_PATH, collection_name="teslaris_publications"):
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_records(self, records):
        """Dodaje listu radova u kolekciju"""
        documents = []
        metadatas = []
        ids = []

        for idx, rec in enumerate(records):
            # Dokument za embedding (naslov + sažetak)
            doc_text = f"Naslov: {rec.get('title', '')}. Sažetak: {rec.get('abstract', '')}"
            documents.append(doc_text)
            
            # Metapodaci
            authors_str = ", ".join(rec.get("authors", [])) if isinstance(rec.get("authors"), list) else str(rec.get("authors", ""))
            metadatas.append({
                "title": rec.get("title", "Nepoznat naslov"),
                "source": rec.get("source", "Nepoznat izvor"),
                "authors": authors_str
            })
            
            # ID zapisa
            ids.append(f"rec_{idx}_{rec.get('id', 'no_id')}")

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"--> Uspešno dodato {len(documents)} radova u kolekciju '{self.collection.name}'.")

    def search(self, query: str, n_results: int = 5):
        print(f"--> [VectorStore] Pretražujem bazu za upit: '{query}'")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        formatted_results = []
        if results and results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(documents)

            for doc, meta in zip(documents, metadatas):
                formatted_results.append({
                    "title": meta.get("title", doc[:60]),
                    "source": meta.get("source", "Nepoznat izvor"),
                    "authors": meta.get("authors", "Nepoznati autori")
                })

        return formatted_results