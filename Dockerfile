# Gunakan Python versi stabil
FROM python:3.9

# Buat folder kerja di server
WORKDIR /app

# Copy file requirements dan install library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode proyek Anda ke server
COPY . .

# Beri izin akses (Penting untuk Hugging Face)
RUN chmod -R 777 .

# Perintah untuk menjalankan Chainlit di Port 7860 (Port standar HF)
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]