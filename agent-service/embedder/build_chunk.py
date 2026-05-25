from metadata.col_desc import COLUMNS_DESC
from metadata.col_enums import COL_ENUMS
from metadata.tables import TABLE_METADATA


def build_overview_chunk(table_name: str) -> str:
    meta = TABLE_METADATA.get(table_name, {})
    lines = [f"TABLE: {table_name}"]
    if meta.get("description"):
        lines.append(f"DESCRIPTION: {meta['description']}")
    if meta.get("relates_to"):
        lines.append(f"JOINS WITH: {', '.join(meta['relates_to'])}")
    return "\n".join(lines)


def build_columns_chunk(table_name: str, columns: list[dict]) -> str:
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
    use_when = TABLE_METADATA.get(table_name, {}).get("use_when", "")
    if not use_when:
        return ""
    return f"TABLE: {table_name}\nUSE WHEN: {use_when}"


def build_chunks_for_table(table_name: str, columns: list[dict]) -> list[dict]:
    """
    Returns up to 3 sub-chunks per table:
        overview   — description + joins
        columns    — column names, types, descriptions, enums
        use_cases  — compact use_when string (unique identity signal)
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
