# scripts/init_db.py

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'attendance.db')

def init_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[*] Memulai inisialisasi arsitektur database EMSY (Single-Batch)...")

    # =====================================================================
    # 1. TABEL MAHASISWA (Sederhana, tanpa Angkatan)
    # NIM diset UNIQUE agar tidak ada duplikasi dalam satu file Excel
    # =====================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            target_kelas TEXT NOT NULL,
            target_rombel TEXT NOT NULL
        )
    ''')

    # =====================================================================
    # 2. TABEL KARTU RFID
    # =====================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rfid_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid_uid TEXT UNIQUE NOT NULL,
            role INTEGER NOT NULL,
            kelas TEXT,
            rombel TEXT
        )
    ''')

    # =====================================================================
    # 3. TABEL PRESENSI HARIAN
    # =====================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presensi_harian (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mahasiswa_id INTEGER NOT NULL,
            tanggal TEXT NOT NULL,
            status TEXT,
            kedatangan TEXT,
            kepulangan TEXT,
            FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa (id)
        )
    ''')

    # =====================================================================
    # 4. TABEL LOG PRESENSI
    # =====================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presensi_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_id INTEGER NOT NULL,
            perubahan TEXT NOT NULL,
            waktu TEXT NOT NULL,
            FOREIGN KEY (attendance_id) REFERENCES presensi_harian (id)
        )
    ''')

    # Injeksi RFID Demo
    print("[*] Memasukkan data konfigurasi awal...")
    cursor.execute("INSERT OR IGNORE INTO rfid_cards (rfid_uid, role, kelas, rombel) VALUES ('290744317040', 1, NULL, NULL)")
    cursor.execute("INSERT OR IGNORE INTO rfid_cards (rfid_uid, role, kelas, rombel) VALUES ('702964954886', 0, 'C', '3')")

    conn.commit()
    conn.close()
    
    print("=====================================================")
    print("[+] SUKSES: Database berhasil diinisialisasi!")
    print("[+] Skema Single-Batch aktif.")
    print("=====================================================")

if __name__ == '__main__':
    init_database()