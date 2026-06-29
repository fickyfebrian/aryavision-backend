# AryaVision Backend API

Backend untuk **Sistem Rekomendasi Produk CCTV** — Tugas Akhir.

Dibangun dengan FastAPI + MySQL + SQLAlchemy dengan arsitektur Clean Architecture.

---

## 🛠 Tech Stack

| Komponen | Teknologi |
|---|---|
| Web Framework | FastAPI |
| Database | MySQL (XAMPP) |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Auth | JWT (python-jose) |
| Validation | Pydantic v2 |
| Server | Uvicorn |

---

## 📁 Struktur Project

```
aryavision-backend/
├── app/
│   ├── api/            → Route definitions (endpoint)
│   ├── core/           → Config, security, JWT utilities
│   ├── database/       → DB connection & session management
│   ├── models/         → SQLAlchemy ORM models
│   ├── schemas/        → Pydantic request/response schemas
│   ├── repositories/   → Database query layer (CRUD operations)
│   ├── services/       → Business logic layer
│   ├── middlewares/    → CORS, error handling
│   └── utils/          → Helper functions (response, dll)
├── alembic/            → Database migrations
├── uploads/            → Uploaded images
├── ml/                 → Machine Learning (Tahap 5)
├── main.py             → Entry point aplikasi
├── requirements.txt    → Python dependencies
├── .env                → Environment variables (jangan commit!)
└── README.md
```

### Alur Request:
```
Route (API) → Service (Business Logic) → Repository (DB Query) → Database
```

---

## ⚙️ Prerequisites

Sebelum menjalankan project, pastikan:
- ✅ Python 3.11+ terinstall
- ✅ XAMPP terinstall dan **MySQL service berjalan**
- ✅ Database `skripsi_cctv` sudah dibuat di phpMyAdmin

---

## 🚀 Cara Menjalankan

### 1. Clone & Masuk ke folder project

```bash
cd aryavision-backend
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

### 3. Aktifkan Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables

Salin `.env.example` menjadi `.env` dan sesuaikan:

```bash
copy .env.example .env
```

Isi `.env` dengan konfigurasi database Anda:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=skripsi_cctv
SECRET_KEY=ganti-dengan-key-yang-aman
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 6. Buat Database di XAMPP

Buka **phpMyAdmin** → buat database baru dengan nama `skripsi_cctv`.

### 7. Jalankan Database Migration (Alembic)

```bash
# Buat migration pertama (setelah models dibuat)
alembic revision --autogenerate -m "initial migration"

# Jalankan migration ke database
alembic upgrade head
```

### 8. Jalankan Server

```bash
# Development (dengan hot-reload)
uvicorn main:app --reload

# Atau langsung
python main.py
```

### 9. Akses Swagger UI

Buka browser dan akses:
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Health Check** : http://localhost:8000/api/health

---

## 📦 Tahapan Pengembangan

| Tahap | Status | Keterangan |
|---|---|---|
| ✅ Tahap 1 | Selesai | Setup Project & Foundation |
| 🔄 Tahap 2 | Dalam pengerjaan | CRUD Produk |
| ⏳ Tahap 3 | Belum | JWT Login Admin |
| ⏳ Tahap 4 | Belum | Upload Image |
| ⏳ Tahap 5 | Belum | Integrasi Machine Learning |

---

## 📐 Format Response

Semua endpoint menggunakan format JSON yang konsisten:

### Success Response:
```json
{
  "success": true,
  "message": "Data berhasil diambil",
  "data": {}
}
```

### Error Response:
```json
{
  "success": false,
  "message": "Data tidak ditemukan",
  "errors": null
}
```

### Paginated Response:
```json
{
  "success": true,
  "message": "Success",
  "data": [],
  "pagination": {
    "total": 100,
    "page": 1,
    "limit": 10,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 🤖 Persiapan Machine Learning

Folder `ml/` akan digunakan untuk integrasi Machine Learning:

```
ml/
├── preprocessing.py    → Data cleaning & feature engineering
├── clustering.py       → K-Means Clustering
└── recommendation.py   → Content-Based Filtering & Cosine Similarity
```

---

## 👤 Author

Ficky Febrian — Tugas Akhir Semester 8
