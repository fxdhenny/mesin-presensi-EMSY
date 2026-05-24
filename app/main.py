# app/main.py
import customtkinter as ctk
import threading
import queue
import time
import os
import sys

# --- TAMBAHKAN INI DI ATAS IMPOR MODUL LOKAL ---
# Memastikan Python mendeteksi folder 'app' sebagai root modul lokal
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Mengimpor modul backend inti
from core.rfid_service import RFIDReader
from core.auth import verifikasi_kartu

# Mengimpor modul database untuk keperluan inisialisasi / pengecekan jalur
from database import queries
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'attendance.db')

# Mengimpor palet warna dan 4 layar UI dari folder terpisah
from ui.colors import C
from ui.screens import WelcomeScreen, RombelSelectScreen, NimListScreen, StudentDetailScreen

class MesinPresensiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EMSY - Sistem Presensi Lab")
        self.geometry("800x480") 
        self.configure(fg_color=C["bg"]) 
        
        # Inisialisasi status hak akses awal (Default: False)
        self.is_master = False
        
        # Inisialisasi antrean komunikasi data RFID
        self.rfid_queue = queue.Queue()
        self.sensor = RFIDReader()
        
        # Menjalankan background thread untuk membaca sensor secara realtime
        self.thread_sensor = threading.Thread(target=self.tugas_satpam_rfid, daemon=True)
        self.thread_sensor.start()

        self.frames = {}
        
        # Pendaftaran Ke-4 Layar Utama UI
        self.frames["welcome"] = WelcomeScreen(self, self.pindah_halaman)
        self.frames["rombel-select"] = RombelSelectScreen(self, self.pindah_halaman)
        self.frames["nim-list"] = NimListScreen(self, self.pindah_halaman)
        self.frames["student-detail"] = StudentDetailScreen(self, self.pindah_halaman)

        # Menampilkan layar pertama saat aplikasi dibuka
        self.tampilkan_halaman("welcome")
        
        # Memulai perulangan pengecekan data dari antrean RFID
        self.after(100, self.periksa_pipa_queue)

    def tampilkan_halaman(self, nama_halaman):
        """Menampilkan halaman tertentu dan menyembunyikan halaman lainnya."""
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[nama_halaman].pack(fill="both", expand=True)
        
    def pindah_halaman(self, nama_halaman, data_tambahan=None):
        """Navigasi antar halaman dengan pembaruan data dinamis."""
        print(f"[*] Navigasi ke: {nama_halaman} | Data: {data_tambahan}")
        if nama_halaman in self.frames:
            # Sembunyikan semua layar terlebih dahulu
            for frame in self.frames.values():
                frame.pack_forget()
                
            layar_tujuan = self.frames[nama_halaman]
            
            # Pemicu Dinamis khusus halaman NIM List agar tombol Back (Master vs Rombel) selalu diperbarui
            if nama_halaman == "nim-list":
                rombel_target = data_tambahan if data_tambahan else layar_tujuan.rombel_aktif
                layar_tujuan.update_data(rombel_target)
            elif hasattr(layar_tujuan, 'update_data') and data_tambahan:
                layar_tujuan.update_data(data_tambahan)
                
            layar_tujuan.pack(fill="both", expand=True)
        else:
            print(f"[-] Halaman '{nama_halaman}' belum diimplementasikan.")

    def tugas_satpam_rfid(self):
        """Thread latar belakang untuk terus membaca kartu dari perangkat MFRC522."""
        while True:
            uid_terbaca = self.sensor.baca_kartu()
            if uid_terbaca:
                self.rfid_queue.put(uid_terbaca)
            time.sleep(0.1)

    def periksa_pipa_queue(self):
        """Memeriksa isi antrean RFID dan menguncinya agar hanya merespon di halaman welcome."""
        try:
            # Mengambil data kartu yang masuk tanpa memblokir aplikasi
            uid_baru = self.rfid_queue.get(block=False)
            
            # Deteksi halaman mana yang saat ini sedang aktif tampil di layar
            halaman_sekarang = None
            for nama_halaman, frame in self.frames.items():
                if frame.winfo_manager():  # Jika frame sedang di-pack/ditampilkan
                    halaman_sekarang = nama_halaman
                    break
            
            # KUNCI FILTER: RFID hanya akan diproses jika layar saat ini adalah 'welcome'
            if halaman_sekarang == "welcome":
                self.proses_login(uid_baru)
            else:
                print(f"[*] RFID Diabaikan! Kartu terdeteksi saat layar berada di: '{halaman_sekarang}'")
                
        except queue.Empty:
            pass
            
        # Mengulang pengecekan pipa antrean secara berkala setiap 100ms
        self.after(100, self.periksa_pipa_queue)

    def proses_login(self, uid):
        """Memproses alur autentikasi kartu RFID yang di-tap."""
        layar_welcome = self.frames["welcome"]
        layar_welcome.ubah_status_scan("Memproses Kartu...", C["tanDark"])
        
        respons = verifikasi_kartu(uid)
        
        if respons["status"] == "dikenal":
            if respons["role"] == "master":
                # Set hak akses sebagai master dan arahkan ke halaman pilih rombel
                self.is_master = True 
                layar_welcome.ubah_status_scan("Akses Master Diberikan!", "green")
                self.after(1000, lambda: self.pindah_halaman("rombel-select", "master"))
            else:
                # Set hak akses sebagai rombel biasa dan langsung lompat ke halaman daftar NIM
                self.is_master = False 
                teks = f"Akses Rombel {respons['kelas']}{respons['rombel']}"
                layar_welcome.ubah_status_scan(teks, "blue")
                self.after(1000, lambda: self.pindah_halaman("nim-list", f"{respons['kelas']}{respons['rombel']}"))
        else:
            layar_welcome.ubah_status_scan("Kartu Tidak Dikenal!", "red")
            
        # Mengembalikan teks petunjuk pemindaian ke kondisi default setelah 3 detik
        self.after(3000, layar_welcome.reset_status_scan)


if __name__ == "__main__":
    app = MesinPresensiApp()
    app.mainloop()