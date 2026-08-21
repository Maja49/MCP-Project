import json
import time
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vector_store import VectorStoreManager

def calculate_precision_at_k(retrieved_ids, relevant_ids, k=5):
    retrieved_at_k = retrieved_ids[:k]
    relevant_retrieved = set(retrieved_at_k).intersection(set(relevant_ids))
    return len(relevant_retrieved) / k

def calculate_recall_at_k(retrieved_ids, relevant_ids, k=5):
    if not relevant_ids:
        return 0.0
    retrieved_at_k = retrieved_ids[:k]
    relevant_retrieved = set(retrieved_at_k).intersection(set(relevant_ids))
    return len(relevant_retrieved) / len(relevant_ids)

def calculate_mrr(retrieved_ids, relevant_ids):
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0

def search_semantic(vm, query_text, top_k=5):
    start_time = time.time()
    results = vm.collection.query(
        query_texts=[query_text],
        n_results=top_k
    )
    latency = (time.time() - start_time) * 1000
    
    retrieved_ids = []
    if results and 'metadatas' in results and results['metadatas']:
        for meta in results['metadatas'][0]:
            retrieved_ids.append(meta.get('source_id', ''))
            
    return retrieved_ids, latency

def search_keyword(vm, query_text, top_k=5):
    start_time = time.time()
    all_docs = vm.collection.get()
    keywords = [w.lower() for w in query_text.split() if len(w) > 2]
    
    scored_docs = []
    if all_docs and 'metadatas' in all_docs:
        for meta in all_docs['metadatas']:
            text = f"{meta.get('title', '')} {meta.get('abstract', '')}".lower()
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scored_docs.append((score, meta.get('source_id', '')))
                
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    retrieved_ids = [doc_id for _, doc_id in scored_docs[:top_k]]
    latency = (time.time() - start_time) * 1000
    
    return retrieved_ids, latency

def run_evaluation():
    base_dir = os.path.dirname(__file__)
    queries_file = os.path.join(base_dir, 'evaluation_queries.json')
    results_dir = os.path.join(base_dir, 'results')
    charts_dir = os.path.join(base_dir, 'charts')
    
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)

    with open(queries_file, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    vm = VectorStoreManager()
    evaluation_results = []

    print("--- POKRETANJE KOMPLETNE EVALUACIJE ---")
    for q in queries:
        q_id = q['query_id']
        q_text = q['query_text']
        category = q['category']
        relevant_ids = q['relevant_ids']

        sem_ids, sem_lat = search_semantic(vm, q_text, top_k=5)
        key_ids, key_lat = search_keyword(vm, q_text, top_k=5)

        evaluation_results.append({
            'query_id': q_id,
            'category': category,
            'sem_p@5': calculate_precision_at_k(sem_ids, relevant_ids, 5),
            'sem_r@5': calculate_recall_at_k(sem_ids, relevant_ids, 5),
            'sem_mrr': calculate_mrr(sem_ids, relevant_ids),
            'sem_latency': sem_lat,
            'key_p@5': calculate_precision_at_k(key_ids, relevant_ids, 5),
            'key_r@5': calculate_recall_at_k(key_ids, relevant_ids, 5),
            'key_mrr': calculate_mrr(key_ids, relevant_ids),
            'key_latency': key_lat
        })

    df = pd.DataFrame(evaluation_results)
    df.to_csv(os.path.join(results_dir, 'keyword_vs_semantic_results.csv'), index=False)

    sns.set_theme(style="whitegrid")

    # Grafikon 1: Metrike
    plt.figure(figsize=(9, 5))
    comparison_df = pd.DataFrame({
        'Metoda': ['Semantic Search', 'Keyword Search'],
        'Recall@5': [df['sem_r@5'].mean(), df['key_r@5'].mean()],
        'MRR': [df['sem_mrr'].mean(), df['key_mrr'].mean()],
        'Precision@5': [df['sem_p@5'].mean(), df['key_p@5'].mean()]
    })
    df_melted = pd.melt(comparison_df, id_vars=['Metoda'], value_vars=['Recall@5', 'MRR', 'Precision@5'])
    sns.barplot(data=df_melted, x='variable', y='value', hue='Metoda', palette='Set2')
    plt.title('Poređenje Performansi: Semantička vs. Leksička Pretraga', fontsize=13, fontweight='bold')
    plt.ylabel('Prosečna Vrednost')
    plt.ylim(0, 1.1)
    plt.savefig(os.path.join(charts_dir, 'keyword_vs_semantic_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # Grafikon 2: Latencija (Vreme odziva)
    plt.figure(figsize=(7, 5))
    lat_df = pd.DataFrame({
        'Metoda': ['Semantic Search', 'Keyword Search'],
        'Prosečna latencija (ms)': [df['sem_latency'].mean(), df['key_latency'].mean()]
    })
    sns.barplot(data=lat_df, x='Metoda', y='Prosečna latencija (ms)', hue='Metoda', palette='Pastel1', legend=False)
    plt.title('Prosečno Vreme Odziva (Latency in ms)', fontsize=13, fontweight='bold')
    plt.savefig(os.path.join(charts_dir, 'search_latency_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"1. Semantic search:")
    print(f"   - Recall@5: {df['sem_r@5'].mean():.4f}")
    print(f"   - MRR:       {df['sem_mrr'].mean():.4f}")
    print(f"   - Precision: {df['sem_p@5'].mean():.4f}")
    print(f"   - Latencija: {df['sem_latency'].mean():.2f} ms")
    print(f"\n2. Lexical (keyword) search:")
    print(f"   - Recall@5: {df['key_r@5'].mean():.4f}")
    print(f"   - MRR:       {df['key_mrr'].mean():.4f}")
    print(f"   - Precision: {df['key_p@5'].mean():.4f}")
    print(f"   - Latencija: {df['key_latency'].mean():.2f} ms")
    print("========================================================================\n")

if __name__ == "__main__":
    run_evaluation()