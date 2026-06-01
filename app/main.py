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
    NimListScreen, StudentDetailScreen, ExportScreen
)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- KONFIGURASI JENDELA UTAMA EMSY ---
        self.title("EMSY - Sistem Presensi Lab")
        self.geometry("800x480")  # Dioptimalkan untuk layar sentuh 5/7 inci
        self.resizable(False, False)
        
        # Standarisasi tema visual CustomTkinter
        ctk.set_appearance_mode("Light")
        
        # --- INISIALISASI VARIABEL LOGIKA & ARSITEKTUR ---
        self.is_master = False          # Melacak status login pengguna aktif
        self.popup_aktif = None         # Menyimpan referensi pop-up update RFID yang sedang terbuka
        self.antrean_rfid = queue.Queue() # Antrean thread-safe penampung ketukan kartu
        self.reader = RFIDReader()      # Instansiasi driver pembaca kartu RFID (Simulasi/Fisik)
        
        # Kamus data untuk menyimpan instance layar aplikasi
        self.frames = {}
        
        # Daftar seluruh layar utama EMSY v2.0 (Skema Single-Batch)
        daftar_layar = {
            "welcome": WelcomeScreen,
            "rombel-select": RombelSelectScreen,
            "update-rfid": UpdateRfidScreen,
            "nim-list": NimListScreen,
            "student-detail": StudentDetailScreen,
            "export-screen": ExportScreen
        }
        
        # Pemanasan Awal (Caching): Render semua layar ke dalam memori
        # master=self langsung dipasangkan pada root window agar tata letak rapi sempurna
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
        """Mengatur perpindahan layar dan menyuntikkan data parameter jika dibutuhkan"""
        frame_target = self.frames.get(nama_halaman)
        if not frame_target:
            print(f"[-] Error: Jendela visual '{nama_halaman}' tidak terdaftar!")
            return
            
        # Jika ada data kiriman (seperti nama rombel atau indeks mahasiswa), suntikkan ke layar target
        if data is not None and hasattr(frame_target, 'update_data'):
            frame_target.update_data(data)
            
        # Sembunyikan seluruh layar yang sedang aktif
        for frame in self.frames.values():
            frame.pack_forget()
            
        # Tampilkan layar target secara penuh
        frame_target.pack(fill="both", expand=True)
        
        # Atur ulang kotak deteksi jika kembali ke gerbang utama
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
                    welcome_frame.ubah_status_scan("Akses Instruktur Diberikan!", "#064e3b") # Hijau
                
                # Jeda 1 detik agar instruktur sempat melihat konfirmasi visual sukses
                self.after(1000, lambda: self.fungsi_navigasi("rombel-select"))
            else:
                self.is_master = False
                print(f"🔵 LOGIN BERHASIL: {respons['pesan']}")
                rombel_nama = f"{respons['kelas']}{respons['rombel']}"
                if welcome_frame:
                    welcome_frame.ubah_status_scan(f"Akses Rombel {rombel_nama} Diberikan!", "#1d4e89") # Biru
                
                # Jeda 1 detik lalu arahkan perwakilan rombel ke daftar NIM anggota kelasnya
                self.after(1000, lambda: self.fungsi_navigasi("nim-list", rombel_nama))
        else:
            print(f"🔴 AKSES DITOLAK: {respons['pesan']}")
            if welcome_frame:
                welcome_frame.ubah_status_scan(respons["pesan"], "#7a2214") # Merah peringatan
                self.after(3000, welcome_frame.reset_status_scan) # Kembalikan teks asli dalam 3 detik

    # =====================================================================
    # LOGIKA MULTI-THREADING MANAJEMEN ANTARAEN SENSOR (ANTI-FREEZE)
    # =====================================================================
    def mulai_thread_rfid(self):
        """Melahirkan thread pekerja di latar belakang khusus untuk membaca kartu rfid"""
        self.thread_pekerja = threading.Thread(target=self.tugas_satpam_rfid, daemon=True)
        self.thread_pekerja.start()

    def tugas_satpam_rfid(self):
        """Loop abadi pembacaan sensor. Berjalan terpisah dari thread visual utama."""
        while True:
            try:
                uid = self.reader.baca_kartu()
                if uid:
                    self.antrean_rfid.put(uid)  # Titipkan UID yang terbaca ke dalam antrean aman
            except Exception as e:
                print(f"[-] Gangguan pembacaan pada komponen thread RFID: {e}")
            time.sleep(0.1)  # Mencegah utilitas CPU melonjak (Overhead Protection)

    def fungsi_cek_antrean_rfid_berkala(self):
        """Listener berkala pada thread utama GUI untuk mengecek pipa antrean data kartu"""
        while not self.antrean_rfid.empty():
            uid_kartu = self.antrean_rfid.get()
            
            # PROTEKSI PENGALIHAN: Jika ada jendela pop-up ganti RFID yang sedang aktif terbuka, 
            # kirim UID ke pop-up tersebut, jangan dilempar ke gerbang login menu utama!
            if hasattr(self, 'popup_aktif') and self.popup_aktif is not None:
                self.popup_aktif.terima_uid_scanned(uid_kartu)
            else:
                self.proses_login(uid_kartu)
                
        # Lakukan pengecekan pipa antrean secara rekursif setiap 100 milidetik
        self.after(100, self.fungsi_cek_antrean_rfid_berkala)

    def pendaftar_popup_aktif(self, instance_popup):
        """Menyediakan gerbang titipan agar pop-up eksternal bisa mendaftarkan dirinya"""
        self.popup_aktif = instance_popup

# =====================================================================
# TITIK EKSEKUSI UTAMA SISTEM EMSY
# =====================================================================
if __name__ == "__main__":
    print("[*] Memulai mesin utama aplikasi EMSY...")
    app = App()
    app.mainloop()