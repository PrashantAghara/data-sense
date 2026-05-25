from metadata.col_desc import COLUMNS_DESC
from metadata.col_enums import COL_ENUMS
from metadata.tables import TABLE_METADATA


def build_overview_chunk(table_name: str) -> str:
    """Description + join relationships — 'what is this table about'."""
    meta = TABLE_METADATA.get(table_name, {})
    lines = [f"TABLE: {table_name}"]

    if meta.get("description"):
        lines.append(f"DESCRIPTION: {meta['description']}")

    if meta.get("relates_to"):
        lines.append(f"JOINS WITH: {', '.join(meta['relates_to'])}")

    return "\n".join(lines)


def build_columns_chunk(table_name: str, columns: list[dict]) -> str:
    """Column names, types, descriptions, and enum values."""
    col_desc = COLUMNS_DESC.get(table_name, {})
    enums = COL_ENUMS.get(table_name, {})
    lines = [f"TABLE: {table_name}", "COLUMNS:"]

    for col in columns:
        name = col["column_name"]
        dtype = col["data_type"]
        desc = col_desc.get(name) or col.get("col_description") or ""
        enum = enums.get(name, "")

        line = f"  {name:<24} {dtype}"
        if desc:
            line += f" -- {desc}"
        if enum:
            line += f" [values: {enum}]"
        lines.append(line)

    return "\n".join(lines)


def build_usecases_chunk(table_name: str) -> str:
    """use_when keywords — the strongest signal for query routing."""
    meta = TABLE_METADATA.get(table_name, {})
    use_when = meta.get("use_when", [])
    if not use_when:
        return ""

    lines = [
        f"TABLE: {table_name}",
        f"USE WHEN: {' | '.join(use_when)}",
    ]
    return "\n".join(lines)


def build_chunks_for_table(table_name: str, columns: list[dict]) -> list[dict]:
    """
    Returns a list of dicts:
        { "table_name": str, "chunk_type": str, "text": str }

    Only non-empty chunks are included.
    chunk_type ∈ { "overview", "columns", "use_cases" }
    """
    candidates = [
        ("overview", build_overview_chunk(table_name)),
        ("columns", build_columns_chunk(table_name, columns)),
        ("use_cases", build_usecases_chunk(table_name)),
    ]
    return [
        {"table_name": table_name, "chunk_type": ctype, "text": text}
        for ctype, text in candidates
        if text.strip()
    ]
