import os
from dotenv import load_dotenv
import psycopg2
import google.generativeai as genai

# Docling
from docling.document_converter import DocumentConverter

# -------------------------------------------------
#            INITIAL SETUP
# -------------------------------------------------
load_dotenv()  # load .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
POSTGRES_URL = os.getenv("POSTGRES_URL")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

if not POSTGRES_URL:
    raise ValueError("POSTGRES_URL not found in .env")

genai.configure(api_key=GEMINI_API_KEY)

# -------------------------------------------------
#            SETUP DATABASE
# -------------------------------------------------
def setup_database(conn):
    EMBEDDING_DIM = 768 
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id SERIAL PRIMARY KEY,
                chunk_text TEXT NOT NULL,
                embedding VECTOR({EMBEDDING_DIM}) NOT NULL,
                filename TEXT NOT NULL,
                split_strategy TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
    conn.commit()
    print("[SETUP] Database schema (pgvector and table) ensured.")

# -------------------------------------------------
#            TEXT EXTRACTION (DOCLING)
# -------------------------------------------------
def extract_text(path: str) -> str:
    print(f"[INFO] Using Docling to extract text from: {path}")
    converter = DocumentConverter()
    result = converter.convert(path)
    text = result.document.export_to_text()
    print(f"[INFO] Extracted {len(text)} characters of text.")
    return text


# -------------------------------------------------
#     FIXED-SIZE CHUNKING WITH OVERLAP
# -------------------------------------------------
def chunk_fixed_with_overlap(text: str, size: int = 500, overlap: int = 100):
    """
    Splits text into chunks of a fixed size, with overlap.
    Example:
        size=500, overlap=100
        Chunk1: 0-500
        Chunk2: 400-900
        Chunk3: 800-1300
    """
    print(f"[INFO] Splitting text into chunks: size={size}, overlap={overlap}")
    chunks = []
    start = 0

    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += size - overlap

    print(f"[INFO] Generated {len(chunks)} chunks.")
    return chunks


# -------------------------------------------------
#           EMBEDDINGS WITH GEMINI
# -------------------------------------------------
def embed_text(text: str):
    response = genai.embed_content(
        model="text-embedding-004",
        content=text
    )
    return response["embedding"]

# -------------------------------------------------
#           SAVE TO POSTGRES
# -------------------------------------------------
def insert_chunk(conn, chunk_text, embedding, filename, strategy):
    embedding_str = f"[{','.join(map(str, embedding))}]"
    
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO document_embeddings
                (chunk_text, embedding, filename, split_strategy, created_at)
            VALUES (%s, %s::vector, %s, %s, NOW())
            """,
            (chunk_text, embedding_str, filename, strategy)
        )
    conn.commit()


# -------------------------------------------------
#           MAIN INDEXING LOGIC
# -------------------------------------------------
def index_file(path: str):
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return

    filename = os.path.basename(path)
    print(f"[INFO] Starting indexing for file: {filename}")

    conn = None
    try:
        text = extract_text(path)
        chunks = chunk_fixed_with_overlap(text, size=500, overlap=100)
        
        conn = psycopg2.connect(POSTGRES_URL)
        setup_database(conn)
        strategy = "fixed_overlap"

        print("[INFO] Generating embeddings and saving to PostgreSQL...")

        for i, chunk in enumerate(chunks, start=1):
            embedding = embed_text(chunk)          
            insert_chunk(conn, chunk, embedding, filename, strategy)
            print(f"[OK] Saved chunk {i}/{len(chunks)}")

        print(f"[DONE] Finished indexing {filename}")

    except psycopg2.Error as e:
        print(f"[CRITICAL ERROR] PostgreSQL error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"[CRITICAL ERROR] An unexpected error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# -------------------------------------------------
#               ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    print("Document Indexer (Gemini + Docling + PostgreSQL)")
    file_path = input("Enter path to PDF/DOCX file: ").strip()

    if not file_path:
        print("[WARN] No file path provided. Exiting.")
    else:
        index_file(file_path)
