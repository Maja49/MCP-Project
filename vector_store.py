import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

class VectorStoreManager:
    def __init__(self, collection_name: str = "teslaris_publications", db_path: str = "./chroma_db"):
        self.db_path = db_path
        self.collection_name = collection_name
        
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_records(self, records: List[Dict[str, Any]]):
        if not records:
            return

        documents = []
        metadatas = []
        ids = []

        for i, rec in enumerate(records):
            text_representation = f"Title: {rec['title']}\nAbstract: {rec['abstract']}\nAuthors: {', '.join(rec['authors'])}"
            documents.append(text_representation)
            
            metadatas.append({
                "source_id": str(rec.get("id", "N/A")),
                "title": str(rec["title"]),
                "abstract": str(rec["abstract"]),
                "authors": ", ".join(rec["authors"]),
                "source": str(rec["source"]),
                "entity_type": str(rec.get("entity_type", "article"))
            })
            
            doc_id = f"{rec['source']}_{rec.get('id', i)}_{i}".replace(" ", "_")
            ids.append(doc_id)

        embeddings = self.model.encode(documents).tolist()

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"--> Uspešno dodato {len(records)} zapisa u kolekciju '{self.collection_name}'.")

    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query_embedding = self.model.encode([query]).tolist()
        
        where_filter = None
        if source and source != "all":
            if source.lower() == "xml":
                where_filter = {"source": "OpenAIRE (XML)"}
            elif source.lower() == "json":
                where_filter = {"source": "SKG-IF (JSON)"}

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=where_filter
        )

        formatted_results = []
        if results and results.get("metadatas"):
            metas = results["metadatas"][0]
            distances = results["distances"][0] if results.get("distances") else [0]*len(metas)
            
            for meta, dist in zip(metas, distances):
                formatted_results.append({
                    "id": meta.get("source_id"),
                    "title": meta.get("title"),
                    "abstract": meta.get("abstract"),
                    "authors": meta.get("authors").split(", ") if meta.get("authors") else [],
                    "source": meta.get("source"),
                    "entity_type": meta.get("entity_type", "article"),
                    "similarity_score": round(1 - dist, 4)
                })

        return formatted_results

    def get_count(self) -> int:
        return self.collection.count()