import os
import time
from core.rfid_service import RFIDReader
from core.auth import verifikasi_kartu
from database import queries

# Setup konfigurasi database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'attendance.db')

def menu_rombel(kelas, rombel):
    """
    Sub-menu ini akan terbuka jika kartu Rombel yang valid berhasil di-tap.
    Menggunakan input berbasis angka (Dial) untuk mencegah salah ketik.
    """
    print(f"\n[*] Menginisialisasi Absensi Kelas {kelas} Rombel {rombel}...")
    berhasil = queries.inisialisasi_presensi(DB_PATH, kelas, rombel)
    
    if not berhasil:
        print("[-] Gagal menyiapkan data presensi. Cek koneksi database.")
        return

    while True:
        print(f"\n{'='*75}")
        print(f"   DAFTAR ABSENSI: KELAS {kelas} - ROMBEL {rombel}")
        print(f"{'='*75}")
        
        data = queries.ambil_data_presensi_hari_ini(DB_PATH, kelas, rombel)
        
        print(f"{'ID DB':<5} | {'No':<2} | {'Nama Mahasiswa':<22} | {'Status':<6} | {'Datang':<12} | {'Pulang':<12}")
        print("-" * 75)
        
        for baris in data:
            id_db, no_absen, nim, nama, status, datang, pulang = baris
            nama_pendek = (nama[:19] + '...') if len(nama) > 22 else nama
            str_datang = datang.title() if datang else "-"
            str_pulang = pulang.title() if pulang else "-"
            print(f"{id_db:<5} | {no_absen:<2} | {nama:<22} | {status.upper():<6} | {str_datang:<12} | {str_pulang:<12}")
            
        print("-" * 75)
        print("[1] Ubah Status Kehadiran")
        print("[2] Ubah Waktu Kedatangan")
        print("[3] Ubah Waktu Kepulangan")
        print("[0] Logout / Tutup Sesi Rombel")
        
        pilihan = input("\nPilih aksi (0/1/2/3): ").strip()
        
        if pilihan == '0':
            print("\n[*] Logout berhasil. Kembali ke mode siaga...")
            break
            
        # Pengecekan IDOR Sentral
        if pilihan in ['1', '2', '3']:
            try:
                id_target = int(input("Masukkan [ID DB] mahasiswa yang ingin diubah: "))
                id_valid_di_layar = [baris[0] for baris in data]
                
                if id_target not in id_valid_di_layar:
                    print(f"[-] AKSES DITOLAK: ID DB {id_target} bukan anggota kelas ini.")
                    time.sleep(1.5)
                    continue
            except ValueError:
                print("[-] Format ID salah. Harap masukkan angka.")
                time.sleep(1.5)
                continue

            # --- OPSI 1: STATUS KEHADIRAN (DIAL ANGKA) ---
            if pilihan == '1':
                print("\nPilih Status Baru:")
                print("[1] Hadir")
                print("[2] Izin")
                print("[3] Sakit")
                print("[4] Alfa")
                sub_pilihan = input("Masukkan angka (1-4): ").strip()
                
                map_status = {'1': 'hadir', '2': 'izin', '3': 'sakit', '4': 'alfa'}
                
                if sub_pilihan in map_status:
                    status_baru = map_status[sub_pilihan]
                    
                    # 1. Update status utama terlebih dahulu
                    queries.update_status_presensi(DB_PATH, id_target, 'status', status_baru)
                    
                    # 2. LOGIKA REVERSE (PEMBERSIHAN DATA)
                    # Jika mahasiswa dialfakan, diizinkan, atau disakitkan, maka 
                    # data kedatangan dan kepulangan WAJIB dihapus (menjadi NULL)
                    if status_baru in ['alfa', 'izin', 'sakit']:
                        queries.update_status_presensi(DB_PATH, id_target, 'kedatangan', None)
                        queries.update_status_presensi(DB_PATH, id_target, 'kepulangan', None)
                        print(f"[+] Status ID {id_target} menjadi {status_baru.upper()}. Data Datang/Pulang di-reset (Kosong).")
                    else:
                        print(f"[+] Status ID {id_target} berhasil diubah menjadi {status_baru.upper()}.")
                else:
                    print("[-] Angka tidak valid! Perubahan dibatalkan.")
                time.sleep(1.5)
            
            # --- OPSI 2: WAKTU KEDATANGAN (DIAL ANGKA) ---
            elif pilihan == '2':
                print("\nPilih Status Kedatangan:")
                print("[1] Tepat Waktu")
                print("[2] Terlambat")
                sub_pilihan = input("Masukkan angka (1-2): ").strip()
                
                map_datang = {'1': 'tepat waktu', '2': 'terlambat'}
                
                if sub_pilihan in map_datang:
                    datang_baru = map_datang[sub_pilihan]
                    queries.update_status_presensi(DB_PATH, id_target, 'kedatangan', datang_baru)
                    # Otomatisasi Status Hadir
                    queries.update_status_presensi(DB_PATH, id_target, 'status', 'hadir')
                    print(f"[+] Kedatangan dicatat: '{datang_baru.title()}'. Status otomatis menjadi HADIR.")
                else:
                    print("[-] Angka tidak valid! Perubahan dibatalkan.")
                time.sleep(1.5)
            
            # --- OPSI 3: WAKTU KEPULANGAN (DIAL ANGKA) ---
            elif pilihan == '3':
                print("\nPilih Status Kepulangan:")
                print("[1] Tepat Waktu")
                print("[2] Lebih Awal")
                sub_pilihan = input("Masukkan angka (1-2): ").strip()
                
                map_pulang = {'1': 'tepat waktu', '2': 'lebih awal'}
                
                if sub_pilihan in map_pulang:
                    pulang_baru = map_pulang[sub_pilihan]
                    # 1. Update status kepulangan
                    queries.update_status_presensi(DB_PATH, id_target, 'kepulangan', pulang_baru)
                    
                    # 2. OTOMATISASI: Memaksa status menjadi hadir
                    queries.update_status_presensi(DB_PATH, id_target, 'status', 'hadir')
                    
                    print(f"[+] Kepulangan dicatat: '{pulang_baru.title()}'. Status otomatis menjadi HADIR.")
                else:
                    print("[-] Angka tidak valid! Perubahan dibatalkan.")
                time.sleep(1.5)
                
        else:
            print("[-] Pilihan tidak dikenali.")
            time.sleep(1)

def jalankan_sistem_cli():
    print("="*60)
    print("      MESIN PRESENSI EMSY - MODE CLI (SIMULASI)")
    print("="*60)
    
    sensor = RFIDReader()
    
    try:
        while True:
            # Karena di laptop, ini akan meminta ketikan UID dari keyboard
            uid = sensor.baca_kartu()
            
            if uid:
                respons = verifikasi_kartu(uid)
                
                if respons["status"] == "dikenal":
                    # --- JIKA KARTU MASTER (DOSEN/INSTRUKTUR) ---
                    if respons["role"] == "master":
                        print(f"\n🟢 AKSES MASTER DIBERIKAN: {respons['pesan']}")
                        print("[*] Memulai proses ekspor data ke Flashdisk...")
                        hasil, pesan_eks = queries.export_to_flashdisk(DB_PATH)
                        if hasil:
                            print(f"[+] EKSPOR SUKSES: {pesan_eks}")
                        else:
                            print(f"[-] EKSPOR GAGAL: {pesan_eks}")
                            
                    # --- JIKA KARTU USER (PERWAKILAN ROMBEL) ---
                    else:
                        print(f"\n🔵 AKSES ROMBEL DIBERIKAN: {respons['pesan']}")
                        menu_rombel(respons["kelas"], respons["rombel"])
                else:
                    print(f"\n🔴 AKSES DITOLAK: {respons['pesan']}")
                    
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n[*] Sistem presensi CLI dimatikan secara aman.")

if __name__ == "__main__":
    jalankan_sistem_cli()