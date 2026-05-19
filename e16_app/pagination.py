from math import ceil

from flask import request


def get_pagination(default_per_page: int = 20, max_per_page: int = 100) -> tuple[int, int]:
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page

    return max(page, 1), min(max(per_page, 1), max_per_page)


def paginate_query(query, page: int, per_page: int) -> dict:
    total = query.order_by(None).count()
    pages = ceil(total / per_page) if total else 1
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "has_prev": page > 1,
        "has_next": page < pages,
    }
