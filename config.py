import os
from pathlib import Path


class Config:

    # === Base paths ===
    PROJECT_ROOT = Path(__file__).resolve().parent
    ICON_DIR = os.path.join(PROJECT_ROOT, "icons")
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    STORED_CHUNK_DIR = os.path.join(PROJECT_ROOT, "doc_chunks")
    UPLOAD_DIR = os.path.join(PROJECT_ROOT, "upload")
    PROMPT_DIR = os.path.join(PROJECT_ROOT, "prompts")
    NLTK_DIR = os.path.join(PROJECT_ROOT, "nltk_words")

    SAVED_ID_PATH = os.path.join(DATA_DIR, "saved_ids.csv")
    SAVED_DATA_PATH = os.path.join(DATA_DIR, "saved_data.txt")

    RAG_PROMPT = os.path.join(PROMPT_DIR, "rag_prompt.txt")
    AGENT_PROMPT = os.path.join(PROMPT_DIR, "agent_prompt.txt")

    UPLOAD_ICON = os.path.join(ICON_DIR, "upload.png")

    COLLECTION_NAME = "qdrant_collection"
    QDRANT_PERSIST_PATH = "qdrant_database"

    # Qdrant DB
    EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"  # "BAAI/bge-base-en-v1.5"
    BATCH_SIZE = 20  # Qdrant batch size
    TOP_K = 4
    ALPHA = 0.5
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

    FILE_EXTENSIONS = [".pdf", ".docx", ".xlsx", ".pptx", ".csv", ".txt", ".json"]

    LLM_MODEL = "gemini-2.5-flash"
    TEMPERATURE = 0.7

    SESSION_ID = "chatbot_user"

