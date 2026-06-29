"""
Response Utility — Format JSON response yang konsisten.

Semua endpoint wajib menggunakan helper ini agar format response
seragam di seluruh aplikasi. Ini juga memudahkan frontend untuk
parsing response karena strukturnya selalu sama.
"""

from typing import Any

from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    """
    Membuat response sukses dengan format standar.

    Format:
    {
        "success": true,
        "message": "...",
        "data": {...}
    }
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )


def error_response(
    message: str = "Internal Server Error",
    status_code: int = 500,
    errors: Any = None,
) -> JSONResponse:
    """
    Membuat response error dengan format standar.

    Format:
    {
        "success": false,
        "message": "...",
        "errors": {...}  ← detail error (opsional)
    }
    """
    content: dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if errors is not None:
        content["errors"] = errors

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def paginated_response(
    items: list[Any],
    total_items: int,
    page: int,
    limit: int,
    message: str = "Success",
) -> JSONResponse:
    """
    Membuat response untuk data yang di-paginate.
    """
    total_pages = (total_items + limit - 1) // limit if limit > 0 else 1

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": message,
            "data": {
                "items": items,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1,
                }
            },
        },
    )
