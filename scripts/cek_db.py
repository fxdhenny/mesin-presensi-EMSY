# scripts/cek_db.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'attendance.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("==========================================")
print("     HASIL DIAGNOSIS DATABASE EMSY        ")
print("==========================================")

# 1. Cek Angkatan Aktif
cursor.execute("SELECT nilai FROM pengaturan WHERE kunci = 'current_batch'")
batch = cursor.fetchone()
print(f"[*] Current Batch  : {batch[0] if batch else 'KOSONG'}")

# 2. Cek Total Mahasiswa
cursor.execute("SELECT COUNT(*) FROM mahasiswa")
total = cursor.fetchone()[0]
print(f"[*] Total Mahasiswa: {total} orang")

# 3. Cek Pemetaan Kelas & Rombel
print("\n[*] Peta Kelas dan Rombel yang tersimpan di SQLite:")
cursor.execute('''
    SELECT angkatan, target_kelas, target_rombel, COUNT(*) 
    FROM mahasiswa 
    GROUP BY angkatan, target_kelas, target_rombel
''')

for row in cursor.fetchall():
    print(f" -> Angkatan: '{row[0]}' | Kelas: '{row[1]}' | Rombel: '{row[2]}' | Jumlah: {row[3]} orang")

print("==========================================")
conn.close()