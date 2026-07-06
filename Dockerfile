# Base image
FROM python:3.11-slim

# Working directory di dalam container
WORKDIR /app

# Copy dan install dependency lebih dulu agar layer di-cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code aplikasi
COPY . .

# Direktori untuk database SQLite (dipetakan ke volume saat Compose)
RUN mkdir -p /app/data

# Port yang diekspos oleh aplikasi
EXPOSE 5000

# Perintah untuk menjalankan aplikasi menggunakan gunicorn (production-ready)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
