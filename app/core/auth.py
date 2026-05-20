import sqlite3
import os

# Melacak lokasi database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'attendance.db')

def verifikasi_kartu(uid_terbaca):
    """
    Mengecek UID ke database dan mengembalikan profil kartu tersebut.
    Return: Dictionary berisi status dan detail kepemilikan kartu.
    """
    if not uid_terbaca:
        return {"status": "error", "pesan": "UID kosong"}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Mencari UID di tabel kartu RFID
        cursor.execute('''
            SELECT role, kelas, rombel 
            FROM rfid_cards 
            WHERE rfid_uid = ?
        ''', (uid_terbaca,))
        
        hasil = cursor.fetchone()
        conn.close()

        # Jika kartu terdaftar di database
        if hasil:
            role, kelas, rombel = hasil
            
            # Role 1 adalah Master (Instruktur), Role 0 adalah User (Perwakilan Rombel)
            if role == 1:
                return {
                    "status": "dikenal",
                    "role": "master",
                    "pesan": "Akses Instruktur Diberikan"
                }
            else:
                return {
                    "status": "dikenal",
                    "role": "user",
                    "kelas": kelas,
                    "rombel": rombel,
                    "pesan": f"Akses Rombel {kelas}-{rombel} Diberikan"
                }
        
        # Jika ada kartu asing (misal: kartu e-toll) yang di-tap
        else:
            return {
                "status": "tidak_dikenal",
                "pesan": "Kartu tidak terdaftar dalam sistem!"
            }

    except Exception as e:
        print(f"[-] Kesalahan sistem saat verifikasi database: {e}")
        return {"status": "error", "pesan": "Gangguan koneksi database"}

# =====================================================================
# BLOK PENGUJIAN FASE 2 (INTEGRASI CLI)
# =====================================================================
if __name__ == '__main__':
    # Mengimpor modul RFID yang sudah kita buat sebelumnya
    # sys.path diatur agar bisa membaca folder app meskipun dieksekusi langsung
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from app.core.rfid_service import RFIDReader
    import time

    print("[*] Memulai Sistem Otentikasi Mode CLI...")
    sensor = RFIDReader()

    try:
        while True:
            uid = sensor.baca_kartu()
            
            if uid:
                print(f"\n[+] Memproses UID: {uid}")
                
                # Lempar UID ke mesin otentikasi
                respons = verifikasi_kartu(uid)
                
                if respons["status"] == "dikenal":
                    if respons["role"] == "master":
                        print(f"🟢 LOGIN BERHASIL: {respons['pesan']}")
                        print("   -> Beralih ke Menu Export/Shutdown...")
                    else:
                        print(f"🔵 LOGIN BERHASIL: {respons['pesan']}")
                        print(f"   -> Menyiapkan absen untuk Kelas {respons['kelas']} Rombel {respons['rombel']}...")
                else:
                    print(f"🔴 AKSES DITOLAK: {respons['pesan']}")
                    
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[*] Mesin presensi CLI dimatikan.")