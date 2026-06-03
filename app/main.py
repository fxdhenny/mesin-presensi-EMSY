# app/main.py
import os
import sys
import time
import queue
import threading
import customtkinter as ctk

# Memastikan Python dapat melacak folder root proyek EMSY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Import modul core dan interface pendukung
from core.rfid_service import RFIDReader
from core.auth import verifikasi_kartu
from ui.screens import (
    WelcomeScreen, RombelSelectScreen, UpdateRfidScreen,
    NimListScreen, StudentDetailScreen, ExportScreen,
    MasterLoginPopup
)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- KONFIGURASI JENDELA UTAMA EMSY ---
        self.title("EMSY - Sistem Presensi Lab")
        self.geometry("800x480")  
        self.resizable(False, False)
        
        # Standarisasi tema visual CustomTkinter
        ctk.set_appearance_mode("Light")
        
        # --- INISIALISASI VARIABEL LOGIKA & ARSITEKTUR ---
        self.is_master = False          
        self.password_file = os.path.join(BASE_DIR, '..', 'data', 'master_password.txt')
        self.master_password = self.load_master_password()
        self.login_popup = None
        self.popup_aktif = None         
        self.antrean_rfid = queue.Queue() 
        self.reader = RFIDReader()      
        
        # =====================================================================
        # FITUR BARU: Variabel pelacak posisi halaman untuk sistem Auto-Block
        # Gerbang awal dimulai dari halaman "welcome"
        # =====================================================================
        self.halaman_aktif = "welcome"
        
        # Kamus data untuk menyimpan instance layar aplikasi
        self.frames = {}
        
        # Daftar seluruh layar utama EMSY v2.0
        daftar_layar = {
            "welcome": WelcomeScreen,
            "rombel-select": RombelSelectScreen,
            "update-rfid": UpdateRfidScreen,
            "nim-list": NimListScreen,
            "student-detail": StudentDetailScreen,
            "export-screen": ExportScreen
        }
        
        # Render semua layar ke dalam memori
        for nama, KelasLayar in daftar_layar.items():
            frame = KelasLayar(master=self, fungsi_navigasi=self.fungsi_navigasi)
            self.frames[nama] = frame
            
        # Tampilkan layar selamat datang sebagai gerbang awal
        self.fungsi_navigasi("welcome")
        
        # Nyalakan thread latar belakang untuk memantau sensor kartu RFID
        self.mulai_thread_rfid()
        
        # Nyalakan fungsi loop pemantau antrean berkala pada main thread GUI
        self.fungsi_cek_antrean_rfid_berkala()

    # =====================================================================
    # MESIN NAVIGASI & DISTRIBUSI DATA ANTAR LAYAR
    # =====================================================================
    def fungsi_navigasi(self, nama_halaman, data=None):
        """Mengatur perpindahan layar dan merekam posisi halaman aktif"""
        frame_target = self.frames.get(nama_halaman)
        if not frame_target:
            print(f"[-] Error: Jendela visual '{nama_halaman}' tidak terdaftar!")
            return
            
        # =====================================================================
        # PERUBAHAN DI SINI: Rekam halaman mana yang saat ini sedang dibuka
        # =====================================================================
        self.halaman_aktif = nama_halaman
        print(f"[*] Navigasi Bergeser ke: {self.halaman_aktif}")
            
        if data is not None and hasattr(frame_target, 'update_data'):
            frame_target.update_data(data)
            
        # Sembunyikan seluruh layar yang sedang aktif
        for frame in self.frames.values():
            frame.pack_forget()
            
        # Tampilkan layar target secara penuh
        frame_target.pack(fill="both", expand=True)
        
        if nama_halaman == "welcome":
            frame_target.reset_status_scan()

    # =====================================================================
    # MESIN VERIFIKASI GERBANG LOGIN KARTU RFID
    # =====================================================================
    def proses_login(self, uid_terbaca):
        """Memproses data UID hasil tap kartu menuju gerbang otentikasi database"""
        print(f"[*] Memproses otentikasi login untuk UID: {uid_terbaca}")
        respons = verifikasi_kartu(uid_terbaca)
        
        welcome_frame = self.frames.get("welcome")
        
        if respons["status"] == "dikenal":
            if respons["role"] == "master":
                self.is_master = True
                print(f"🟢 LOGIN BERHASIL: {respons['pesan']}")
                if welcome_frame:
                    welcome_frame.ubah_status_scan("Akses Instruktur Diberikan!", "#064e3b")
                self.after(1000, lambda: self.fungsi_navigasi("rombel-select"))
            else:
                self.is_master = False
                print(f"🔵 LOGIN BERHASIL: {respons['pesan']}")
                rombel_nama = f"{respons['kelas']}{respons['rombel']}"
                if welcome_frame:
                    welcome_frame.ubah_status_scan(f"Akses Rombel {rombel_nama} Diberikan!", "#1d4e89")
                self.after(1000, lambda: self.fungsi_navigasi("nim-list", rombel_nama))
        else:
            print(f"🔴 AKSES DITOLAK: {respons['pesan']}")
            if welcome_frame:
                welcome_frame.ubah_status_scan(respons["pesan"], "#7a2214")
                self.after(3000, welcome_frame.reset_status_scan)

    # =====================================================================
    # POP-UP LOGIN MASTER DARI TOMBOL 'M' DI LAYAR AWAL
    # =====================================================================
    def buka_popup_login_master(self):
        if self.login_popup and self.login_popup.winfo_exists():
            self.login_popup.lift()
            return
        self.login_popup = MasterLoginPopup(self)
        self.login_popup.grab_set()

    def validate_master_password(self, password):
        return password == self.master_password

    def set_master_password(self, new_password):
        self.master_password = new_password
        try:
            with open(self.password_file, 'w', encoding='utf-8') as f:
                f.write(new_password)
        except Exception as e:
            print(f"[-] Gagal menyimpan password master: {e}")

    def load_master_password(self):
        default_password = "terimakasihC3"
        try:
            if not os.path.exists(self.password_file):
                os.makedirs(os.path.dirname(self.password_file), exist_ok=True)
                with open(self.password_file, 'w', encoding='utf-8') as f:
                    f.write(default_password)
                return default_password

            with open(self.password_file, 'r', encoding='utf-8') as f:
                password = f.read().strip()
                return password if password else default_password
        except Exception as e:
            print(f"[-] Gagal memuat password master: {e}")
            return default_password

    # =====================================================================
    # LOGIKA MULTI-THREADING MANAJEMEN ANTARAEN SENSOR (ANTI-FREEZE)
    # =====================================================================
    def mulai_thread_rfid(self):
        self.thread_pekerja = threading.Thread(target=self.tugas_satpam_rfid, daemon=True)
        self.thread_pekerja.start()

    def tugas_satpam_rfid(self):
        while True:
            try:
                uid = self.reader.baca_kartu()
                if uid:
                    self.antrean_rfid.put(uid)  
            except Exception as e:
                print(f"[-] Gangguan pembacaan pada komponen thread RFID: {e}")
            time.sleep(0.1)  

    # =====================================================================
    # PENGENDALI FILTER PIPELINE (GERBANG AUTO-BLOCK)
    # =====================================================================
    def fungsi_cek_antrean_rfid_berkala(self):
        """Listener berkala pada thread utama GUI dengan proteksi Sesi Terkunci"""
        while not self.antrean_rfid.empty():
            uid_kartu = self.antrean_rfid.get()
            
            # PROTEKSI 1: Jika ada jendela pop-up ganti RFID yang terbuka, data harus tetap lolos
            if hasattr(self, 'popup_aktif') and self.popup_aktif is not None:
                self.popup_aktif.terima_uid_scanned(uid_kartu)
                
            # PROTEKSI 2 (CRITICAL AUTO-BLOCK): Jika ada user sedang aktif di dalam sistem 
            # (di luar layar welcome), langsung abaikan kartu baru yang ditempelkan!
            elif self.halaman_aktif != "welcome":
                print(f"🔒 [AUTO-BLOCK] Kartu {uid_kartu} DIABAIKAN. Sesi aktif di halaman '{self.halaman_aktif}'!")
                continue  # 'continue' akan membuang kartu ini dan langsung memeriksa antrean selanjutnya
                
            # KONDISI 3: Jalankan login normal jika aplikasi sedang stand-by di layar welcome
            else:
                self.proses_login(uid_kartu)
                
        self.after(100, self.fungsi_cek_antrean_rfid_berkala)

    def pendaftar_popup_aktif(self, instance_popup):
        self.popup_aktif = instance_popup

if __name__ == "__main__":
    print("[*] Memulai mesin utama aplikasi EMSY...")
    app = App()
    app.mainloop()