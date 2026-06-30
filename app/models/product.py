"""
SQLAlchemy Model — Tabel Products.

Model ini mendefinisikan skema tabel 'products' yang akan dibuat
oleh Alembic migration. Mewarisi Base dari database/connection.py
agar Alembic bisa mendeteksinya secara otomatis.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Product(Base):
    """
    Model untuk tabel 'products'.

    Tabel ini adalah tabel utama aplikasi yang berisi data CCTV
    yang sudah bersih dan siap digunakan oleh API maupun Machine Learning.

    Data asalnya dari tabel 'produk' (raw dataset hasil scraping Tokopedia)
    yang sudah dipreprocess oleh script scripts/import_dataset.py.
    """

    __tablename__ = "products"

    # Primary Key — Auto Increment
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    # Nama lengkap produk dari Tokopedia
    product_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,  # Untuk mempercepat pencarian berdasarkan nama
    )

    # URL halaman produk di Tokopedia
    product_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # URL gambar produk
    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Brand produk (diekstrak dari nama produk — EZVIZ, Hikvision, dll)
    brand: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # Kategori produk (Indoor, Outdoor, PTZ, dll — akan diisi manual/ML nanti)
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # Harga dalam Rupiah (integer, tanpa titik/koma)
    # Contoh: Rp999.000 → 999000
    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Rating produk (0.0 - 5.0)
    rating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Jumlah produk terjual
    # Contoh: "100+ terjual" → 100, "1rb+ terjual" → 1000
    sold: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=0,
    )

    # Deskripsi produk (untuk Machine Learning — Content-Based Filtering)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Cluster (untuk Machine Learning — Clustering)
    cluster: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Timestamps — otomatis diisi oleh database
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name='{self.product_name[:40]}...' price={self.price}>"
