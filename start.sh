#!/bin/bash

echo "=========================================="
echo "    MEMULAI SISTEM PRESENSI EMSY...       "
echo "=========================================="

# 1. Pindah ke direktori tempat script ini berada (Root Proyek)
# Ini mencegah error jika Anda memanggil script dari direktori lain
cd "$(dirname "$0")"

# 2. Periksa apakah folder Virtual Environment (venv) sudah ada
if [ ! -d "venv" ]; then
    echo "[*] Virtual environment tidak ditemukan."
    echo "[+] Membuat Virtual Environment (venv) baru..."
    python3 -m venv venv
    echo "[+] Venv berhasil dibuat!"
else
    echo "[*] Virtual environment sudah tersedia."
fi

# 3. Aktifkan Virtual Environment
echo "[*] Mengaktifkan Virtual Environment..."
source venv/bin/activate

# 4. Instal pustaka yang dibutuhkan (pip akan otomatis mendeteksi jika sudah terinstal)
echo "[*] Memeriksa dan memperbarui pustaka Python..."
pip install --upgrade pip  # Memastikan pip versi terbaru
pip install customtkinter openpyxl

# (Opsional: Jika Anda memakai pustaka RFID tambahan seperti mfrc522 atau pyserial, tambahkan di atas)

# 5. Jalankan aplikasi utama
echo "=========================================="
echo "[+] Menjalankan app/main.py..."
echo "=========================================="
python3 app/main.py

# 6. Nonaktifkan venv setelah aplikasi ditutup
deactivate