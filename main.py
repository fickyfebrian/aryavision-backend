"""
Main Application Entry Point — AryaVision Backend.

File ini adalah titik masuk utama aplikasi FastAPI.
Di sini semua komponen dirakit:
- FastAPI instance dibuat
- Middleware didaftarkan
- Router (endpoint) didaftarkan
- Exception handler didaftarkan
- Startup/shutdown event dikelola
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import health, product, ml
from app.core.config import settings
from app.database.connection import check_database_connection
from app.middlewares.exception_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager untuk startup dan shutdown.

    Menggunakan asynccontextmanager (modern approach di FastAPI 0.95+)
    untuk menggantikan on_event("startup") yang deprecated.
    """
    # ===== STARTUP =====
    print(f"\n[STARTUP] Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    db_ok = check_database_connection()
    if db_ok:
        print("[OK] Database connection: Connected")
    else:
        print("[WARNING] Database connection: FAILED - Pastikan XAMPP MySQL sedang berjalan!")

    print(f"[INFO] Swagger UI  : http://localhost:8000/docs")
    print(f"[INFO] ReDoc       : http://localhost:8000/redoc")
    print(f"[INFO] Health Check: http://localhost:8000/api/health\n")

    yield  # Aplikasi berjalan di sini

    # ===== SHUTDOWN =====
    print(f"\n[SHUTDOWN] Shutting down {settings.APP_NAME}...")


# Buat instance FastAPI dengan metadata untuk Swagger UI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## AryaVision Backend API

Backend untuk Sistem Rekomendasi Produk CCTV.

### Fitur:
- 📦 CRUD Produk CCTV
- 🔐 JWT Authentication
- 🤖 Machine Learning Integration (coming soon)

### Tech Stack:
- **FastAPI** — Web framework
- **SQLAlchemy** — ORM
- **MySQL** — Database
- **JWT** — Authentication
    """,
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ===== MIDDLEWARE =====

# CORS — mengizinkan frontend mengakses API ini
# Di production, ganti allow_origins dengan domain frontend yang spesifik
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Saat development, izinkan semua origin
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE, dll
    allow_headers=["*"],       # Authorization, Content-Type, dll
)

# ===== STATIC FILES =====
# Melayani file dari folder uploads/ (untuk gambar produk nantinya)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ===== EXCEPTION HANDLERS =====
register_exception_handlers(app)

# ===== ROUTERS =====
# Semua router di-prefix dengan /api untuk versioning yang jelas
app.include_router(health.router, prefix="/api")
app.include_router(product.router, prefix="/api")
app.include_router(ml.router, prefix="/api")

# Nanti akan ditambahkan:
# app.include_router(auth.router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — redirect info ke docs."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,   # Hot-reload saat development
        log_level="info",
    )
