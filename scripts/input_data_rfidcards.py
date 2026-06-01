# scripts/input_data_rfidcards.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'attendance.db')

def seed_rfid():
    if not os.path.exists(DB_PATH):
        print("[-] Error: Database belum ada. Jalankan init_db.py terlebih dahulu.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    daftar_kartu = [
        ('290744317040', 1, None, None), # Master
        ('702964954886', 0, 'A', '1'),
        ('1044274421078', 0, 'A', '2'),
        ('908933593632', 0, 'A', '3'),
        ('152366292474', 0, 'B', '1'),
        ('769218647486', 0, 'B', '2'),
        ('222911733083', 0, 'B', '3'),
        ('426334887351', 0, 'C', '1'),
        ('633357145590', 0, 'C', '2'),
        ('83477339586', 0, 'C', '3')
    ]

    rfid_berhasil, rfid_dilewati = 0, 0
    
    print("[*] Menginjeksi data aset fisik Kartu RFID...")
    for kartu in daftar_kartu:
        try:
            cursor.execute('''
                INSERT INTO rfid_cards (rfid_uid, role, kelas, rombel)
                VALUES (?, ?, ?, ?)
            ''', kartu)
            rfid_berhasil += 1
        except sqlite3.IntegrityError:
            rfid_dilewati += 1

    conn.commit()
    conn.close()

    print(f"[+] Selesai: {rfid_berhasil} kartu masuk, {rfid_dilewati} dilewati (duplikat).")

if __name__ == '__main__':
    seed_rfid()