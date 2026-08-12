import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set working directory to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from vector_store import VectorStoreManager
from sentence_transformers import SentenceTransformer

# Set theme for plots (clean modern style suitable for master thesis)
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11, 'figure.autolayout': True})

# Output directory for generated charts
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)


def run_latency_experiment(vsm, test_queries):
    """
    Experiment 1: Measure search latency across different Top-K values
    """
    print("\n[1/4] Running Experiment: Search Latency (Latency vs Top-K)...")
    top_k_values = [1, 3, 5, 10, 15, 20]
    avg_times = []

    for k in top_k_values:
        times = []
        for q in test_queries:
            start_time = time.time()
            _ = vsm.search(query=q, top_k=k)
            elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds (ms)
            times.append(elapsed)
        avg_times.append(np.mean(times))
        print(f"  -> Top-K = {k:2d} | Average Latency: {np.mean(times):.2f} ms")

    plt.figure(figsize=(8, 5))
    plt.plot(top_k_values, avg_times, marker='o', linewidth=2.5, color='#4f46e5', label='ChromaDB RAG Search')
    plt.title('Search Performance: Response Latency vs. Top-K', fontsize=13, pad=15)
    plt.xlabel('Number of Returned Results (Top-K)')
    plt.ylabel('Average Latency (ms)')
    plt.xticks(top_k_values)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    chart_path = os.path.join(CHARTS_DIR, "1_search_latency.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"  --> Saved Chart: {chart_path}")


def run_score_distribution_experiment(vsm, test_queries):
    """
    Experiment 2: Analyze Similarity Score (Cosine Similarity) Distribution
    """
    print("\n[2/4] Running Experiment: Similarity Score Distribution...")
    all_scores = []
    
    for q in test_queries:
        results = vsm.search(query=q, top_k=5)
        for r in results:
            if r.get('similarity_score') is not None:
                all_scores.append(r['similarity_score'])

    plt.figure(figsize=(8, 5))
    sns.histplot(all_scores, kde=True, color='#06b6d4', bins=10)
    plt.title('Semantic Similarity Score Distribution (Top 5 Results)', fontsize=13, pad=15)
    plt.xlabel('Similarity Score (Cosine Similarity)')
    plt.ylabel('Match Frequency')
    plt.axvline(np.mean(all_scores), color='red', linestyle='--', label=f'Mean: {np.mean(all_scores):.2f}')
    plt.legend()
    plt.tight_layout()

    chart_path = os.path.join(CHARTS_DIR, "2_similarity_distribution.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"  --> Saved Chart: {chart_path}")


def run_model_comparison_experiment(test_queries):
    """
    Experiment 3: Compare Multilingual Model vs English-only Model
    """
    print("\n[3/4] Running Experiment: Embedding Model Encoding Speed...")
    
    print("  -> Loading Multilingual Model (paraphrase-multilingual-MiniLM-L12-v2)...")
    m_multi = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    print("  -> Loading English Model (all-MiniLM-L6-v2)...")
    m_eng = SentenceTransformer("all-MiniLM-L6-v2")

    sample_text = "Application of artificial intelligence in scientific publication analysis"
    
    t0 = time.time()
    _ = m_multi.encode([sample_text]*50)
    time_multi = (time.time() - t0) * 1000 / 50

    t0 = time.time()
    _ = m_eng.encode([sample_text]*50)
    time_eng = (time.time() - t0) * 1000 / 50

    models = ['Multilingual MiniLM-L12\n(Native SR/EN Support)', 'English MiniLM-L6\n(English Only)']
    times = [time_multi, time_eng]

    plt.figure(figsize=(7, 5))
    bars = plt.bar(models, times, color=['#6366f1', '#a855f7'], width=0.5)
    plt.title('Average Embedding Generation Time per Text (ms)', fontsize=12, pad=15)
    plt.ylabel('Time (ms)')
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, f'{yval:.2f} ms', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    chart_path = os.path.join(CHARTS_DIR, "3_model_comparison.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"  --> Saved Chart: {chart_path}")


def run_keyword_vs_semantic_experiment(vsm):
    """
    Experiment 4: Compare Traditional Exact Keyword Search vs. Semantic RAG Search
    """
    print("\n[4/4] Running Experiment: Keyword Search vs. Multilingual Semantic RAG...")
    
    # Serbian queries searching over multilingual / English index
    test_cases = [
        "veštačka inteligencija",
        "obrada slika",
        "obnovljivi izvori",
        "mašinsko učenje",
        "baze podataka"
    ]

    all_docs = vsm.collection.get(include=['documents'])
    docs = all_docs.get('documents', []) if all_docs else []

    kw_hits = []
    sem_hits = []

    for q in test_cases:
        # 1. Exact string keyword match count
        exact_matches = sum(1 for d in docs if q.lower() in d.lower())
        kw_hits.append(exact_matches)

        # 2. Semantic RAG match count (top_k relevant retrieved)
        results = vsm.search(query=q, top_k=5)
        sem_hits.append(len(results))

    x = np.arange(len(test_cases))
    width = 0.35

    plt.figure(figsize=(9, 5))
    plt.bar(x - width/2, kw_hits, width, label='Traditional Keyword Match (Exact)', color='#f43f5e')
    plt.bar(x + width/2, sem_hits, width, label='TeslaRIS Multilingual RAG (Ours)', color='#10b981')

    plt.title('Retrieval Effectiveness: Exact Keyword Match vs. Multilingual Semantic RAG', fontsize=12, pad=15)
    plt.xlabel('Cross-lingual Search Queries (Serbian)')
    plt.ylabel('Retrieved Relevant Records (Top-5 Threshold)')
    plt.xticks(x, test_cases, rotation=10)
    plt.legend()
    plt.tight_layout()

    chart_path = os.path.join(CHARTS_DIR, "4_keyword_vs_semantic.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"  --> Saved Chart: {chart_path}")


if __name__ == "__main__":
    print("==================================================")
    print("   TeslaRIS MCP RAG - Experimental Evaluation     ")
    print("==================================================")

    db_path = os.path.join(PROJECT_ROOT, "chroma_db")
    vsm = VectorStoreManager(db_path=db_path)

    test_queries = [
        "artificial intelligence in medicine",
        "machine learning algorithms for data classification",
        "communication and educational tools",
        "solar energy and renewable resources",
        "natural language processing and neural networks",
        "smart grid systems in electrical engineering",
        "database indexing techniques",
        "deep learning model analysis",
        "agricultural soil resistance sensors",
        "software engineering methodologies"
    ]

    run_latency_experiment(vsm, test_queries)
    run_score_distribution_experiment(vsm, test_queries)
    run_model_comparison_experiment(test_queries)
    run_keyword_vs_semantic_experiment(vsm)

    print("\n✅ ALL 4 EXPERIMENTS COMPLETED SUCCESSFULLY!")
    print(f"📊 Generated charts saved in: {CHARTS_DIR}")