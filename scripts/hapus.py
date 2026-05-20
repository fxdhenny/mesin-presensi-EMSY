import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'attendance.db')

# =========================================================
# KONEKSI DATABASE
# =========================================================
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Aktifkan foreign key agar proses drop/delete teratur
    cursor.execute("PRAGMA foreign_keys = ON;")
    print(f"[*] Database terhubung di:\n    {DB_PATH}\n")

except sqlite3.Error as e:
    print("[!] Gagal koneksi database")
    print("[ERROR]", e)
    exit()

# =========================================================
# 1. TAMPILKAN DAFTAR TABEL SEBELUM DIHAPUS
# =========================================================
cursor.execute("""
    SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
""")
tabel_sebelum = cursor.fetchall()
print("[*] Daftar tabel saat ini:")
for t in tabel_sebelum:
    print(f"    - {t[0]}")
print("-" * 50)

# =========================================================
# 2. PROSES PENGHAPUSAN TABEL (Beri proteksi DROP tunggal)
# =========================================================
print("[*] Memulai penghapusan tabel...")
try:
    # Wajib hapus presensi_logs duluan karena dia anak/dependen dari presensi_harian
    cursor.execute("DROP TABLE IF EXISTS presensi_logs;")
    print("[+] Tabel 'presensi_logs' berhasil dihapus.")
    
    cursor.execute("DROP TABLE IF EXISTS presensi_harian;")
    print("[+] Tabel 'presensi_harian' berhasil dihapus.")
    
    # Commit perubahan
    conn.commit()
    print("\n[+] SEMUA TABEL TARGET BERHASIL DIHAPUS!")

except sqlite3.Error as err:
    print(f"[!] Terjadi kesalahan saat menghapus tabel: {err}")
    conn.rollback()

# =========================================================
# 3. VERIFIKASI AKHIR
# =========================================================
print("-" * 50)
cursor.execute("""
    SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
""")
tabel_sesudah = cursor.fetchall()
print("[*] Daftar tabel tersisa di database:")
if not tabel_sesudah:
    print("    (Kosong - semua tabel terhapus)")
else:
    for t in tabel_sesudah:
        print(f"    - {t[0]}")

conn.close()