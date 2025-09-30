from typing import List, Tuple


def build_where(filters: List[str]) -> str:
    if not filters:
        return ""
    return " WHERE " + " AND ".join(filters)


def paginate_sql(limit: int, offset: int) -> str:
    return f" ORDER BY 1 DESC LIMIT {int(limit)} OFFSET {int(offset)}"

