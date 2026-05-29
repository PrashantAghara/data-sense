import os
import psycopg2
from pgvector.psycopg2 import register_vector
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from build_chunk import build_chunks_for_table
from chunks import upsert_chunk, ensure_schema_chunks_table
from table_cols import fetch_table_columns
from test_embedder import run_retrieval_test

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 32


def load_embeddings():
    load_dotenv()
    db_params = {
        "dbname": "data-sense-db",
        "user": os.getenv("POSTGRES_USERNAME"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": "5432",
    }
    os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")

    print("Loading embedding model …")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True, "batch_size": BATCH_SIZE},
    )
    print("  ✓ model ready")

    print("Connecting to PostgreSQL …")
    conn = psycopg2.connect(**db_params)
    register_vector(conn)
    cur = conn.cursor()
    print("  ✓ connected")

    print("\n[1/4] Setting up schema_chunks table …")
    ensure_schema_chunks_table(conn)

    print("\n[2/4] Fetching columns from information_schema …")
    tables = fetch_table_columns(cur)
    print(f"  ✓ {len(tables)} tables: {', '.join(sorted(tables))}")

    print("\n[3/4] Building sub-chunks …")
    all_chunks: list[dict] = []  # {table_name, chunk_type, text}
    for table_name, columns in sorted(tables.items()):
        sub = build_chunks_for_table(table_name, columns)
        all_chunks.extend(sub)
        sizes = ", ".join(f"{c['chunk_type']}={len(c['text'])}ch" for c in sub)
        print(f"  ✓ {table_name:<20} → {len(sub)} chunks  [{sizes}]")

    print(f"\n  Total sub-chunks to embed: {len(all_chunks)}")

    print(f"\n[4/4] Embedding {len(all_chunks)} chunks …")
    texts = [c["text"] for c in all_chunks]
    vectors = embeddings.embed_documents(texts)
    print(f"  ✓ {len(vectors)} vectors ready (dim={len(vectors[0])})")

    print("\nUpserting into schema_chunks …")
    ok, failed = 0, 0
    for chunk, vector in zip(all_chunks, vectors):
        if upsert_chunk(
            cur, chunk["table_name"], chunk["chunk_type"], chunk["text"], vector
        ):
            conn.commit()
            ok += 1
            print(f"  ✓ {chunk['table_name']:<20} [{chunk['chunk_type']}]")
        else:
            conn.rollback()
            failed += 1

    print(f"\n  DONE — {ok} indexed, {failed} failed")

    run_retrieval_test(conn, embeddings)

    cur.close()
    conn.close()


if __name__ == "__main__":
    load_embeddings()
