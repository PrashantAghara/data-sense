TEST_QUESTIONS = [
    "How many customers bought Electronics using UPI?",
    "Which seller has the most returned items?",
    "Show monthly revenue trend for 2023",
    "Which products are low on stock in Mumbai warehouse?",
    "Top 10 customers by total spending",
    "Average EMI tenure for orders above 10000 rupees",
    "How many orders were cancelled in Maharashtra?",
    "Which Paytm wallet users bought Fashion products?",
]

TOP_K = 5

# Weighted aggregation: use_cases chunks count more than generic columns chunk.
# CASE weights mirror how much each chunk type narrows the query routing decision.
RETRIEVAL_SQL = """
    SELECT
        table_name,
        ROUND(
            MAX(
                (1 - (embedding <=> %s::vector)) *
                CASE chunk_type
                    WHEN 'use_cases' THEN 1.4
                    WHEN 'overview'  THEN 1.1
                    ELSE                  1.0
                END
            )::numeric, 4
        ) AS weighted_similarity
    FROM schema_chunks
    GROUP BY table_name
    ORDER BY MAX(
        (1 - (embedding <=> %s::vector)) *
        CASE chunk_type
            WHEN 'use_cases' THEN 1.4
            WHEN 'overview'  THEN 1.1
            ELSE                  1.0
        END
    ) DESC
    LIMIT %s
"""


def run_retrieval_test(conn, embeddings):
    cur = conn.cursor()

    # ── sanity check ──────────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM schema_chunks")
    total_rows = cur.fetchone()[0]
    print(f"\n  schema_chunks total rows: {total_rows}")

    cur.execute(
        "SELECT table_name, chunk_type, LEFT(ddl_chunk, 100) FROM schema_chunks LIMIT 6"
    )
    print("  Sample rows:")
    for row in cur.fetchall():
        print(f"    [{row[1]:10}] {row[0]:<20} {row[2]!r}")

    # ── retrieval test ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  Retrieval Test  (top_k={TOP_K}, weighted by chunk_type)")
    print("=" * 60)

    for question in TEST_QUESTIONS:
        vec = embeddings.embed_query(question)
        cur.execute(RETRIEVAL_SQL, (vec, vec, TOP_K))
        rows = cur.fetchall()

        if not rows:
            print(f"\nQ: {question[:65]}\n   ✗ No results")
            continue

        max_sim = float(rows[0][1])
        flag = "  ⚠ LOW" if max_sim < 0.35 else ""
        result = "  →  ".join(f"{r[0]} ({r[1]})" for r in rows)
        q_short = question[:65] + "…" if len(question) > 65 else question
        print(f"\nQ: {q_short}")
        print(f"   {result}{flag}")

    cur.close()
