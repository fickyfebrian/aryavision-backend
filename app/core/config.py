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
    DB_PASSWORD: str = ""
    DB_NAME: str = "skripsi_cctv"

    # --- JWT ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

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
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton instance — import ini di tempat lain untuk mengakses config
settings = Settings()
