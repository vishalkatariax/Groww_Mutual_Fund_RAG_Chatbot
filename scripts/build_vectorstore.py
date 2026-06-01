"""
Run at Docker build time to:
1. Pre-download the BGE model into the image cache
2. Build ChromaDB from data/processed/chunks.json

This avoids cold-start delays on Railway.
"""
import json
import sys
from pathlib import Path

# Support both Docker (/app) and local execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sentence_transformers import SentenceTransformer

print("Downloading BGE model...")
SentenceTransformer("BAAI/bge-small-en-v1.5")
print("BGE model cached")

from app.phase1.subphase_1_2_chunking_embedding.embedder import EmbeddingPipeline
from app.phase1.subphase_1_2_chunking_embedding.vector_store import VectorStore

chunks_path = PROJECT_ROOT / "data" / "processed" / "chunks.json"
with open(chunks_path) as f:
    chunks = json.load(f)

vs = VectorStore()
if vs.collection.count() == 0:
    embedder = EmbeddingPipeline()
    chunks = embedder.generate_embeddings(chunks)
    vs.add_chunks(chunks)
    print(f"Built ChromaDB: {vs.collection.count()} chunks")
else:
    print(f"ChromaDB already has {vs.collection.count()} chunks")
