DDL_SCHEMA_CHUNKS = """
CREATE TABLE IF NOT EXISTS schema_chunks (
    id          SERIAL      PRIMARY KEY,
    table_name  TEXT        NOT NULL,
    chunk_type  TEXT        NOT NULL,
    ddl_chunk   TEXT        NOT NULL,
    embedding   vector(384) NOT NULL,
    indexed_at  TIMESTAMP   NOT NULL DEFAULT now(),
    UNIQUE (table_name, chunk_type)
);
CREATE INDEX IF NOT EXISTS idx_schema_chunks_embedding
    ON schema_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);
"""

UPSERT_SQL = """
    INSERT INTO schema_chunks (table_name, chunk_type, ddl_chunk, embedding, indexed_at)
    VALUES (%s, %s, %s, %s, now())
    ON CONFLICT (table_name, chunk_type) DO UPDATE SET
        ddl_chunk  = EXCLUDED.ddl_chunk,
        embedding  = EXCLUDED.embedding,
        indexed_at = now()
"""


def ensure_schema_chunks_table(conn):
    cur = conn.cursor()
    cur.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE  table_name = 'schema_chunks'
                AND    column_name = 'chunk_type'
            ) THEN
                -- already migrated, nothing to do
            ELSE
                DROP TABLE IF EXISTS schema_chunks;
            END IF;
        END;
        $$;
    """)
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    for stmt in DDL_SCHEMA_CHUNKS.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
    cur.close()
    print("✓ schema_chunks table ready")


def upsert_chunk(
    cur, table_name: str, chunk_type: str, chunk: str, vector: list[float]
) -> bool:
    try:
        cur.execute(UPSERT_SQL, (table_name, chunk_type, chunk, vector))
        return True
    except Exception as exc:
        print(f"✗ DB error for '{table_name}/{chunk_type}': {exc}")
        return False
