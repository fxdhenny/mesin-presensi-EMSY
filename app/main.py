# app/main.py
import customtkinter as ctk
import threading
import queue
import time
import os

# Mengimpor modul backend inti
from core.rfid_service import RFIDReader
from core.auth import verifikasi_kartu

# Mengimpor palet warna dan 4 layar UI dari folder terpisah
from ui.colors import C
from ui.screens import WelcomeScreen, RombelSelectScreen, NimListScreen, StudentDetailScreen

class MesinPresensiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EMSY - Sistem Presensi Lab")
        self.geometry("800x480") 
        self.configure(fg_color=C["bg"]) 
        
        self.rfid_queue = queue.Queue()
        self.sensor = RFIDReader()
        
        self.thread_sensor = threading.Thread(target=self.tugas_satpam_rfid, daemon=True)
        self.thread_sensor.start()

        self.frames = {}
        
        # Pendaftaran Ke-4 Layar (Bersih tanpa duplikasi)
        self.frames["welcome"] = WelcomeScreen(self, self.pindah_halaman)
        self.frames["rombel-select"] = RombelSelectScreen(self, self.pindah_halaman)
        self.frames["nim-list"] = NimListScreen(self, self.pindah_halaman)
        self.frames["student-detail"] = StudentDetailScreen(self, self.pindah_halaman)

        # Menampilkan layar pertama dan memulai loop pengecekan pipa
        self.tampilkan_halaman("welcome")
        self.after(100, self.periksa_pipa_queue)

    def tampilkan_halaman(self, nama_halaman):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[nama_halaman].pack(fill="both", expand=True)
        
    def pindah_halaman(self, nama_halaman, data_tambahan=None):
        print(f"[*] Navigasi ke: {nama_halaman} | Data: {data_tambahan}")
        if nama_halaman in self.frames:
            # Sembunyikan semua layar
            for frame in self.frames.values():
                frame.pack_forget()
                
            layar_tujuan = self.frames[nama_halaman]
            
            # TRIGGER DINAMIS: Jika layar tujuan punya fungsi update_data, kirim datanya!
            if hasattr(layar_tujuan, 'update_data') and data_tambahan:
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
            self.proses_login(uid_baru)
        except queue.Empty:
            pass
        self.after(100, self.periksa_pipa_queue)

    def proses_login(self, uid):
        layar_welcome = self.frames["welcome"]
        layar_welcome.ubah_status_scan("Memproses Kartu...", C["tanDark"])
        
        respons = verifikasi_kartu(uid)
        
        if respons["status"] == "dikenal":
            if respons["role"] == "master":
                layar_welcome.ubah_status_scan("Akses Master Diberikan!", "green")
                self.after(1000, lambda: self.pindah_halaman("rombel-select", "master"))
            else:
                teks = f"Akses Rombel {respons['kelas']}{respons['rombel']}"
                layar_welcome.ubah_status_scan(teks, "blue")
                self.after(1000, lambda: self.pindah_halaman("nim-list", f"{respons['kelas']}{respons['rombel']}"))
        else:
            layar_welcome.ubah_status_scan("Kartu Tidak Dikenal!", "red")
            
        self.after(3000, layar_welcome.reset_status_scan)


if __name__ == "__main__":
    app = MesinPresensiApp()
    app.mainloop()