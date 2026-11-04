from fastapi import Query
from typing import NamedTuple

class Pagination(NamedTuple):
    limit: int
    offset: int

def pagination_params(
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
):
    return Pagination(limit=limit, offset=offset)