from fastapi import Query
from typing import Optional


# ---------- Dependency for Pagination ----------
def pagination_params(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    search: Optional[str] = None
) -> dict:
    return {"page": page, "page_size": page_size, "search": search}