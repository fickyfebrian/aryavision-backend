"""
Database Connection — SQLAlchemy Engine & Session.

Menggunakan pola Session Dependency Injection agar:
1. Setiap request mendapat session yang fresh
2. Session otomatis di-close setelah request selesai (menggunakan try/finally)
3. Mudah di-mock saat unit testing
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Engine adalah koneksi pool ke database.
# pool_pre_ping=True akan melakukan ping ke DB sebelum menggunakan koneksi
# dari pool, untuk menghindari error "MySQL server has gone away"
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle koneksi setiap 1 jam
    echo=settings.DEBUG,  # Log semua SQL query saat DEBUG mode aktif
)

# SessionLocal adalah factory untuk membuat session baru
# autocommit=False → kita kontrol commit secara manual (best practice)
# autoflush=False  → flush tidak otomatis terjadi sebelum query
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    Base class untuk semua SQLAlchemy Model.

    Semua model akan mewarisi class ini, sehingga Alembic
    bisa mendeteksi semua model secara otomatis.
    """
    pass


def get_db():
    """
    Dependency Injection untuk database session.

    Digunakan dengan FastAPI Depends():
        def my_endpoint(db: Session = Depends(get_db)):
            ...

    Session otomatis di-close setelah request selesai,
    baik sukses maupun terjadi exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Mengecek apakah koneksi ke database berhasil.
    Digunakan saat startup aplikasi.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
