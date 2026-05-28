# app/main.py
import customtkinter as ctk
import threading
import queue
import time
import os
import sys

# --- MENGUNCI PATH ROOT DIREKTORI ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(ROOT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from core.rfid_service import RFIDReader
from core.auth import verifikasi_kartu
from app.database import queries

DB_PATH = os.path.join(BASE_DIR, 'data', 'attendance.db')

from ui.colors import C
# Menambahkan ExportScreen ke dalam import
from ui.screens import WelcomeScreen, RombelSelectScreen, NimListScreen, StudentDetailScreen, ExportScreen

class MesinPresensiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EMSY - Sistem Presensi Lab")
        self.geometry("800x480") 
        self.configure(fg_color=C["bg"]) 
        
        self.is_master = False
        self.rfid_queue = queue.Queue()
        self.sensor = RFIDReader()
        
        self.thread_sensor = threading.Thread(target=self.tugas_satpam_rfid, daemon=True)
        self.thread_sensor.start()

        self.frames = {}
        self.frames["welcome"] = WelcomeScreen(self, self.pindah_halaman)
        self.frames["rombel-select"] = RombelSelectScreen(self, self.pindah_halaman)
        self.frames["nim-list"] = NimListScreen(self, self.pindah_halaman)
        self.frames["student-detail"] = StudentDetailScreen(self, self.pindah_halaman)
        # Mendaftarkan halaman ExportScreen
        self.frames["export-screen"] = ExportScreen(self, self.pindah_halaman)

        self.tampilkan_halaman("welcome")
        self.after(100, self.periksa_pipa_queue)

    def tampilkan_halaman(self, nama_halaman):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[nama_halaman].pack(fill="both", expand=True)
        
    def pindah_halaman(self, nama_halaman, data_tambahan=None):
        print(f"[*] Navigasi ke: {nama_halaman} | Data: {data_tambahan}")
        if nama_halaman in self.frames:
            for frame in self.frames.values():
                frame.pack_forget()
                
            layar_tujuan = self.frames[nama_halaman]
            
            if nama_halaman == "nim-list":
                if data_tambahan:
                    rombel_target = data_tambahan
                elif layar_tujuan.rombel_aktif:
                    rombel_target = layar_tujuan.rombel_aktif
                else:
                    rombel_target = "A1" 
                    
                layar_tujuan.update_data(rombel_target)
            elif hasattr(layar_tujuan, 'update_data') and data_tambahan:
                layar_tujuan.update_data(data_tambahan)
                
            layar_tujuan.pack(fill="both", expand=True)
        else:
            print(f"[-] Halaman '{nama_halaman}' belum diimplementasikan.")

    def tugas_satpam_rfid(self):
        while True:
            uid_terbaca = self.sensor.baca_kartu()
            if uid_terbaca:
                self.rfid_queue.put(uid_terbaca)
            time.sleep(0.1)

    def periksa_pipa_queue(self):
        try:
            uid_baru = self.rfid_queue.get(block=False)
            halaman_sekarang = None
            for nama_halaman, frame in self.frames.items():
                if frame.winfo_manager(): 
                    halaman_sekarang = nama_halaman
                    break
            
            if halaman_sekarang == "welcome":
                self.proses_login(uid_baru)
            else:
                print(f"[*] RFID Diabaikan! Kartu terdeteksi saat layar berada di: '{halaman_sekarang}'")
        except queue.Empty:
            pass
        self.after(100, self.periksa_pipa_queue)

    def proses_login(self, uid):
        layar_welcome = self.frames["welcome"]
        layar_welcome.ubah_status_scan("Memproses Kartu...", "#967e67")
        respons = verifikasi_kartu(uid)
        
        if respons["status"] == "dikenal":
            if respons["role"] == "master":
                self.is_master = True 
                layar_welcome.ubah_status_scan("Akses Master Diberikan!", "green")
                self.after(1000, lambda: self.pindah_halaman("rombel-select", "master"))
            else:
                self.is_master = False 
                teks = f"Akses Rombel {respons['kelas']}{respons['rombel']}"
                layar_welcome.ubah_status_scan(teks, "blue")
                self.after(1000, lambda: self.pindah_halaman("nim-list", f"{respons['kelas']}{respons['rombel']}"))
        else:
            layar_welcome.ubah_status_scan("Kartu Tidak Dikenal!", "red")
            
        self.after(3000, layar_welcome.reset_status_scan)

if __name__ == "__main__":
    app = MesinPresensiApp()
    app.mainloop()