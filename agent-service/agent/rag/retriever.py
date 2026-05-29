import psycopg2
from collections import defaultdict
from pgvector.psycopg2 import register_vector
from core.db import db_params
from core.llm import embeddings

RETRIEVE_SQL = """
    SELECT
        table_name,
        ROUND(
            MAX(
                (1 - (embedding <=> %s::vector)) *
                CASE chunk_type
                    WHEN 'overview' THEN 1.4
                    WHEN 'use_cases'  THEN 1.1
                    ELSE                  1.0
                END
            )::numeric, 4
        ) AS weighted_similarity
    FROM schema_chunks
    GROUP BY table_name
    ORDER BY MAX(
        (1 - (embedding <=> %s::vector)) *
        CASE chunk_type
            WHEN 'overview' THEN 1.4
            WHEN 'use_cases'  THEN 1.1
            ELSE                  1.0
        END
    ) DESC
    LIMIT %s
"""


def get_all_tables() -> list[str]:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT table_name FROM schema_chunks ORDER BY table_name")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables


def retrieve_relevant_schema(question: str, top_k: int = 5) -> str:
    vec = embeddings.embed_query(question)

    conn = psycopg2.connect(**db_params)
    register_vector(conn)
    cur = conn.cursor()

    # Step 1 — Get top-k tables by weighted similarity
    cur.execute(RETRIEVE_SQL, (vec, vec, top_k))
    top_tables = cur.fetchall()

    print("[RAG] Top tables by weighted similarity:")
    for table, score in top_tables:
        print(f"  {table}: {score}")

    # Step 2 — Fetch all chunks for those tables
    table_names = [row[0] for row in top_tables]
    cur.execute(
        """
        SELECT table_name, chunk_type, ddl_chunk
        FROM schema_chunks
        WHERE table_name = ANY(%s)
        ORDER BY table_name, chunk_type
        """,
        (table_names,),
    )
    chunks = cur.fetchall()
    conn.close()

    # Step 3 — Group by table, preserve relevance order
    table_chunks = defaultdict(list)
    for table, chunk_type, ddl_chunk in chunks:
        table_chunks[table].append(f"-- [{chunk_type}]\n{ddl_chunk}")

    return "\n\n".join(
        f"=== {table} ===\n" + "\n\n".join(table_chunks[table]) for table in table_names
    )
