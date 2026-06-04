#!/bin/bash

echo "=========================================="
echo "    MEMULAI SISTEM PRESENSI EMSY...       "
echo "=========================================="

# 1. Pindah ke direktori tempat script ini berada
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

# 4. Instal pustaka yang dibutuhkan 
echo "[*] Memeriksa dan memperbarui pustaka Python..."
pip install --upgrade pip

# =========================================================
# PERUBAHAN DI SINI: Menambahkan mfrc522 dan spidev
# =========================================================
pip install customtkinter openpyxl mfrc522 spidev

# 5. Jalankan aplikasi utama
echo "=========================================="
echo "[+] Menjalankan app/main.py..."
echo "=========================================="
python3 app/main.py

# 6. Nonaktifkan venv setelah aplikasi GUI ditutup (tanda X ditekan)
deactivate