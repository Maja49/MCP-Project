import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vector_store import VectorStoreManager

vm = VectorStoreManager()
results = vm.collection.get(limit=10)

for i in range(len(results['ids'])):
    meta = results['metadatas'][i]
    print(f"ID: {meta.get('source_id')} | Title: {meta.get('title')}")