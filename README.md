# Notes API — Tugas Praktikum Integrasi Docker, Orkestrasi, dan CI/CD

Aplikasi REST API sederhana untuk mencatat *notes* (catatan), dibangun dengan
Flask dan SQLite. Proyek ini dibuat untuk memenuhi Tugas Praktikum
Terintegrasi mata kuliah **Komputasi Awan (Cloud Computing)** — Pertemuan 14:
integrasi Docker, Docker Compose (orkestrasi sederhana), dan CI/CD dengan
GitHub Actions.

## Struktur Proyek

```
notes-api/
├── app/
│   ├── __init__.py      # application factory
│   ├── db.py            # helper koneksi & query SQLite
│   └── routes.py        # endpoint API (health check, CRUD notes)
├── tests/
│   └── test_app.py      # automated test (pytest)
├── nginx/
│   └── default.conf     # konfigurasi reverse proxy
├── wsgi.py              # entrypoint untuk gunicorn
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .github/
│   └── workflows/
│       └── ci.yml       # pipeline GitHub Actions
└── README.md
```

## Teknologi

- **Bahasa/Framework**: Python 3.11, Flask
- **Database**: SQLite dengan Docker volume persisten (`notes-data`)
- **Reverse proxy**: Nginx (service kedua pada Docker Compose, nilai tambah)
- **Testing**: pytest (database SQLite in-memory, tanpa dependensi eksternal)
- **Container**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Endpoint API

| Method | Endpoint       | Deskripsi                       |
|--------|----------------|----------------------------------|
| GET    | `/health`      | Health check, mengembalikan `{"status": "healthy"}` |
| GET    | `/notes`       | Menampilkan seluruh catatan      |
| POST   | `/notes`       | Membuat catatan baru (`title`, `content`) |
| GET    | `/notes/<id>`  | Menampilkan satu catatan         |
| DELETE | `/notes/<id>`  | Menghapus satu catatan           |

## Menjalankan Secara Lokal (tanpa Docker)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py
```

Aplikasi berjalan di `http://localhost:5000`.

## Menjalankan Automated Test

```bash
pip install -r requirements.txt
pytest -v
```

Semua test menggunakan SQLite in-memory sehingga dapat dijalankan tanpa
menyalakan container maupun database eksternal terlebih dahulu.

## Membangun dan Menjalankan dengan Docker (satu container)

```bash
docker build -t aplikasi-mahasiswa:v1 .
docker images
docker run -d --name aplikasi-mahasiswa -p 8080:5000 aplikasi-mahasiswa:v1
docker ps
curl http://localhost:8080/health
```

## Menjalankan dengan Docker Compose (Aplikasi + Reverse Proxy)

`docker-compose.yml` mendefinisikan dua service:

- **app** — container Flask/gunicorn, menyimpan data pada file SQLite di
  Docker volume `notes-data` (data tetap ada walau container dihentikan),
  dilengkapi `healthcheck` pada endpoint `/health`.
- **proxy** — Nginx sebagai reverse proxy sederhana yang meneruskan
  permintaan pada port `8080` ke service `app`, dan baru berjalan setelah
  `app` berstatus *healthy* (`depends_on: condition: service_healthy`).

```bash
docker compose up -d
docker compose ps
curl http://localhost:8080/health

curl -X POST http://localhost:8080/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Belajar Docker", "content": "Integrasi Docker dan CI/CD"}'

curl http://localhost:8080/notes
docker compose down
```

Untuk menghapus juga data yang tersimpan, gunakan `docker compose down -v`.

## CI/CD dengan GitHub Actions

Setiap `push` atau `pull request` ke branch `main` akan menjalankan pipeline
`.github/workflows/ci.yml` yang terdiri dari:

1. Checkout source code
2. Setup Python 3.11
3. Instalasi dependency (`pip install -r requirements.txt`)
4. Menjalankan automated test (`pytest -v`)
5. Membangun Docker image (`docker build`)

Jika test gagal, pipeline berhenti pada tahap tersebut (status **failed**)
dan Docker image tidak dibangun — ini membuktikan fungsi *quality gate*
dari pipeline CI/CD.

## Simulasi Pipeline Gagal dan Berhasil

Untuk mendemonstrasikan pipeline sebagai quality gate:

1. Ubah salah satu assertion di `tests/test_app.py` menjadi salah (misalnya
   `assert response.status_code == 999`), lalu commit & push. Pipeline akan
   gagal pada langkah *Run automated test*. Ambil screenshot/link log ini.
2. Kembalikan assertion ke nilai yang benar, commit & push kembali. Pipeline
   akan berhasil (semua langkah berwarna hijau). Ambil screenshot/link log
   ini juga.

## Hubungan Docker, Docker Compose, dan CI/CD

- **Docker** membungkus aplikasi beserta seluruh dependensinya ke dalam satu
  image yang konsisten di komputer manapun.
- **Docker Compose** mengorkestrasikan beberapa service (aplikasi dan
  reverse proxy) secara deklaratif melalui satu file konfigurasi dan satu
  perintah (`docker compose up`), termasuk urutan start-up (`depends_on`)
  dan pemulihan otomatis (`restart policy`).
- **CI/CD (GitHub Actions)** mengotomatisasi pengujian dan pembangunan image
  setiap kali ada perubahan kode, sehingga kesalahan terdeteksi lebih awal
  sebelum image benar-benar digunakan (*quality gate*).

Ketiganya saling melengkapi: Docker menstandarkan lingkungan eksekusi,
Compose mengelola bagaimana beberapa container tersebut bekerja sama, dan
CI/CD memastikan setiap perubahan pada kode sudah teruji sebelum menjadi
image baru.

## Catatan Keamanan

Proyek ini tidak menyimpan kredensial rahasia apa pun di repository. Jika
menambahkan fitur yang memerlukan API key, token, atau password, gunakan
**GitHub Secrets** dan environment variable, jangan menuliskannya langsung
di kode maupun file konfigurasi yang diunggah ke repository.
