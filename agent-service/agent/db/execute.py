import psycopg2
from core.db import db_params


def execute_sql(query: str):
    """Execute a SQL query and return (rows, error)."""
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute(query)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        conn.close()
        return rows, None
    except Exception as e:
        return None, str(e)
