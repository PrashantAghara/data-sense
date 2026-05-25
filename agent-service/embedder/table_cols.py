from metadata.tables import TABLE_METADATA


def fetch_table_columns(cur, schema: str = "public") -> dict[str, list[dict]]:
    cur.execute(
        """
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            col_description(
                (c.table_schema || '.' || c.table_name)::regclass,
                c.ordinal_position
            ) AS col_description
        FROM information_schema.columns c
        WHERE c.table_schema = %s AND c.table_name   != 'schema_chunks'
        ORDER BY c.table_name, c.ordinal_position
    """,
        (schema,),
    )

    tables: dict[str, list[dict]] = {}
    for row in cur.fetchall():
        tname, col_name, dtype, nullable, comment = row
        tables.setdefault(tname, []).append(
            {
                "column_name": col_name,
                "data_type": dtype,
                "is_nullable": nullable,
                "col_description": comment,
            }
        )
    known = set(TABLE_METADATA.keys())
    found = set(tables.keys())
    skipped = found - known
    missing = known - found
    if skipped:
        print(f"Tables in DB without metadata (skipped): {', '.join(sorted(skipped))}")
    if missing:
        print(f"Tables in metadata not found in DB:     {', '.join(sorted(missing))}")
    return {t: cols for t, cols in tables.items() if t in known}
