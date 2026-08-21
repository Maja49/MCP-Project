# TeslaRIS Multilingual MCP RAG Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Protocol](https://img.shields.io/badge/protocol-Model_Context_Protocol_(MCP)-green.svg)](https://modelcontextprotocol.io/)
[![Vector Database](https://img.shields.io/badge/vector_db-ChromaDB-red.svg)](https://www.trychroma.com/)

This repository contains the implementation and evaluation of a **FastMCP RAG Server** designed for real-time semantic retrieval of scientific research metadata from the **TeslaRIS (CRIS)** database.
The system provides LLM AI agents (within a ReAct framework) with secure, structured access to research papers, researchers, and scientific projects while overcoming cross-lingual and morphological language barriers.

## Key Features

* **FastMCP Protocol Integration**: Standardized communication with AI agents via JSON-RPC 2.0 over a stdio interface.
* **Semantic & Cross-Lingual Search**: Leverages the `paraphrase-multilingual-MiniLM-L12-v2` SBERT model to map Serbian and English queries/documents into a shared vector space.
* **Efficient Vector Storage**: Powered by ChromaDB with optimized indexing and memory management.
* **Comprehensive Evaluation Pipeline**: Automated evaluation scripts measuring standard IR metrics ($Precision@K$, $Recall@K$, $MRR$) and response latency.

## Tech Stack

* **Language**: Python 3.10+
* **MCP Framework**: FastMCP
* **Vector Database**: ChromaDB
* **Embeddings**: Sentence-Transformers (SBERT)
* **Visualization & Evaluation**: Matplotlib, Seaborn, NumPy, Pandas
