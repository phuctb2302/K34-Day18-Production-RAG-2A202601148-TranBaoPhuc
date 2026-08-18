"""Shared configuration for Lab 18."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys & LLM Config ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or GROQ_API_KEY

is_groq = bool(
    GROQ_API_KEY
    or OPENAI_API_KEY.startswith("gsk_")
    or "groq" in os.getenv("OPENAI_BASE_URL", "").lower()
)
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL", "https://api.groq.com/openai/v1" if is_groq else None
)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama-3.1-8b-instant" if is_groq else "gpt-4o-mini")

# Đồng bộ vào os.environ để các thư viện ngoài cũng nhận diện được
if GROQ_API_KEY and not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = GROQ_API_KEY
if OPENAI_BASE_URL and not os.getenv("OPENAI_BASE_URL"):
    os.environ["OPENAI_BASE_URL"] = OPENAI_BASE_URL


def get_llm_client():
    """Get an OpenAI client configured for OpenAI or Groq/OpenRouter."""
    api_key = GROQ_API_KEY or OPENAI_API_KEY
    if not api_key:
        return None
    from openai import OpenAI

    kwargs = {"api_key": api_key}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL
    return OpenAI(**kwargs)


# --- Qdrant ---
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "lab18_production"
NAIVE_COLLECTION = "lab18_naive"

# --- Embedding ---
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# --- Chunking ---
HIERARCHICAL_PARENT_SIZE = 2048
HIERARCHICAL_CHILD_SIZE = 256
SEMANTIC_THRESHOLD = 0.85

# --- Search ---
BM25_TOP_K = 20
DENSE_TOP_K = 20
HYBRID_TOP_K = 20
RERANK_TOP_K = 3

# --- Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEST_SET_PATH = os.path.join(os.path.dirname(__file__), "test_set.json")
