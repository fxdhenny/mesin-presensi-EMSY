import sqlite3
import os

# Menentukan jalur absolut ke database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'attendance.db')

def init_database():
    # Pastikan folder data/ sudah ada
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[*] Memulai inisialisasi arsitektur database EMSY...")

    # =====================================================================
    # 1. TABEL PENGATURAN GLOBAL (Untuk menyimpan Current Batch)
    # =====================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pengaturan (
            kunci TEXT PRIMARY KEY,
            nilai TEXT NOT NULL
        )
    ''')

    # =====================================================================
    # 2. TABEL MAHASISWA
    # Menggunakan UNIQUE(nim, angkatan) untuk mengizinkan mahasiswa yang 
    # mengulang kelas agar bisa di-import lagi dengan id yang baru.
    # =====================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT NOT NULL,
            nama TEXT NOT NULL,
            angkatan TEXT NOT NULL,
            target_kelas TEXT NOT NULL,
            target_rombel TEXT NOT NULL,
            UNIQUE(nim, angkatan)
        )
    ''')

    # =====================================================================
    # 3. TABEL KARTU RFID
    # Sesuai kesepakatan, RFID tidak memiliki kolom 'angkatan'. 
    # Kartu ini bersifat permanen untuk rombel fisik.
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
    # 4. TABEL PRESENSI HARIAN
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
    # 5. TABEL LOG PRESENSI
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

    # =====================================================================
    # INJEKSI DATA AWAL (SEEDING)
    # =====================================================================
    print("[*] Memasukkan data konfigurasi awal...")

    # Set Angkatan Aktif default (Bisa diubah oleh Master nantinya)
    cursor.execute('''
        INSERT OR IGNORE INTO pengaturan (kunci, nilai) 
        VALUES ('current_batch', 'ATMI59')
    ''')

    # Set Kartu Master Demo
    cursor.execute('''
        INSERT OR IGNORE INTO rfid_cards (rfid_uid, role, kelas, rombel) 
        VALUES ('290744317040', 1, NULL, NULL)
    ''')

    # Set Kartu Rombel Demo
    cursor.execute('''
        INSERT OR IGNORE INTO rfid_cards (rfid_uid, role, kelas, rombel) 
        VALUES ('702964954886', 0, 'C', '3')
    ''')

    conn.commit()
    conn.close()
    print("=====================================================")
    print("[+] SUKSES: Database berhasil diinisialisasi!")
    print(f"[+] Lokasi DB : {DB_PATH}")
    print("[+] Konsep Current Batch dan Skema Lifecycle aktif.")
    print("=====================================================")

if __name__ == '__main__':
    init_database()