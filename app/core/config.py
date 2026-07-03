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
    DB_HOST: str = "db.withdmwtkaupnyxcndsw.supabase.co"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "Ikikasep11!"
    DB_NAME: str = "postgres"

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
        f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
        f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        "?sslmode=require"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton instance — import ini di tempat lain untuk mengakses config
settings = Settings()
