"""
Exception Handlers — Global Error Handling.

Mendaftarkan exception handler di level aplikasi agar semua error
(baik yang kita throw maupun error tak terduga) selalu dikembalikan
dalam format JSON yang konsisten.

Ini mencegah FastAPI mengembalikan HTML error page atau format
yang tidak sesuai ekspektasi frontend.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


def register_exception_handlers(app: FastAPI) -> None:
    """
    Mendaftarkan semua global exception handlers ke instance FastAPI.
    Dipanggil sekali saat aplikasi di-setup di main.py.
    """

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """
        Handler untuk HTTPException bawaan FastAPI agar outputnya konsisten
        dengan format aplikasi.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "errors": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handler untuk Pydantic validation error (400 Bad Request).
        Terjadi saat input dari client tidak sesuai schema yang didefinisikan.
        """
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation Error: Data yang dikirim tidak valid",
                "errors": errors,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """
        Handler untuk error dari SQLAlchemy (500 Internal Server Error).
        Error detail disembunyikan dari client demi keamanan.
        """
        # Log error di server (akan terlihat di terminal)
        print(f"[DATABASE ERROR] {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Database error terjadi. Silakan coba lagi.",
                "errors": None,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handler untuk semua exception yang tidak tertangani (500 Internal Server Error).
        Safety net terakhir agar tidak ada error yang bocor ke client.
        """
        print(f"[UNHANDLED ERROR] {type(exc).__name__}: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error. Silakan coba lagi.",
                "errors": None,
            },
        )
