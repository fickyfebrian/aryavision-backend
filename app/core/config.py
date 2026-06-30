"""
Konfigurasi aplikasi menggunakan Pydantic Settings.

Pydantic Settings secara otomatis membaca nilai dari file .env,
sehingga tidak ada hardcoded config di dalam kode.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Semua konfigurasi aplikasi dipusatkan di sini.
    Nilai dibaca otomatis dari environment variables / file .env.
    """

    # --- Database ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASS: str = ""
    DB_NAME: str = "products"

    # --- JWT ---
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # --- App ---
    APP_NAME: str = "AryaVision API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    @property
    def DATABASE_URL(self) -> str:
        """
        Membangun Database URL secara dinamis dari komponen-komponennya.
        Menggunakan PyMySQL sebagai driver karena lebih ringan dan pure Python.
        """
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton instance — import ini di tempat lain untuk mengakses config
settings = Settings()
