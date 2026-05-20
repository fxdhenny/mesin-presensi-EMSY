import customtkinter as ctk
import threading
import queue
import time
import os

# Mengimpor modul inti yang sudah kita buat
from core.rfid_service import RFIDReader
from core.auth import verifikasi_kartu

# Setup konfigurasi database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'attendance.db')

class MesinPresensiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- KONFIGURASI JENDELA UTAMA ---
        self.title("EMSY - Sistem Presensi Lab")
        self.geometry("800x480") # Resolusi standar layar sentuh Raspberry Pi
        
        # --- INISIALISASI PIPA KOMUNIKASI (QUEUE) ---
        self.rfid_queue = queue.Queue()
        
        # --- INISIALISASI SENSOR ---
        self.sensor = RFIDReader()
        
        # --- PEMBUATAN BACKGROUND THREAD ---
        # Daemon=True artinya jika jendela GUI di-close (X), thread satpam ini ikut mati otomatis
        self.thread_sensor = threading.Thread(target=self.tugas_satpam_rfid, daemon=True)
        self.thread_sensor.start()

        # --- PLACEHOLDER GUI (Untuk Divisi UI) ---
        # (Teman Anda nantinya akan menghapus label ini dan menggantinya dengan layout login_window.py)
        self.label_status = ctk.CTkLabel(self, text="Silakan Tap Kartu Anda...", font=("Helvetica", 24))
        self.label_status.pack(expand=True)

        # --- MEMULAI LOOP PEMANTAUAN PIPA ---
        # Menjalankan fungsi periksa_pipa pertama kali setelah 100ms
        self.after(100, self.periksa_pipa_queue)

    def tugas_satpam_rfid(self):
        """
        Fungsi ini berjalan di dimensi lain (Background Thread).
        Tugasnya hanya satu: Menunggu kartu, membaca, dan melempar UID ke dalam pipa.
        """
        while True:
            # Fungsi ini akan 'membeku' (blocking) menunggu kartu, tapi GUI tetap aman!
            uid_terbaca = self.sensor.baca_kartu()
            
            if uid_terbaca:
                # Masukkan UID ke dalam pipa untuk dikirim ke Main Thread
                self.rfid_queue.put(uid_terbaca)
            
            # Istirahat sejenak agar CPU Raspberry Pi tidak overheat
            time.sleep(0.1)

    def periksa_pipa_queue(self):
        """
        Fungsi ini berjalan di dimensi GUI (Main Thread).
        Tugasnya melihat apakah ada 'paket' UID yang dikirim dari dimensi Background.
        """
        try:
            # Coba ambil isi pipa tanpa memaksa (block=False)
            uid_baru = self.rfid_queue.get(block=False)
            
            # Jika ada kartu, oper ke sistem otentikasi
            self.proses_login(uid_baru)
            
        except queue.Empty:
            # Jika pipa kosong, tidak apa-apa, lewati saja
            pass
        
        # ULANGI fungsi ini setiap 100 milidetik (Ini adalah pengganti while True di GUI)
        self.after(100, self.periksa_pipa_queue)

    def proses_login(self, uid):
        """
        Menerima UID dari antrean dan memproses logikanya ke database.
        """
        # Panggil fungsi auth.py yang sudah kita buat sebelumnya
        respons = verifikasi_kartu(uid)
        
        # Contoh mengubah tampilan GUI berdasarkan hasil otentikasi
        if respons["status"] == "dikenal":
            if respons["role"] == "master":
                self.label_status.configure(text="Login Master Berhasil!", text_color="green")
                # Nantinya di sini memanggil: self.tampilkan_halaman_master()
            else:
                teks = f"Login Rombel {respons['kelas']}-{respons['rombel']} Berhasil!"
                self.label_status.configure(text=teks, text_color="blue")
                # Nantinya di sini memanggil: self.tampilkan_halaman_rombel()
        else:
            self.label_status.configure(text="Kartu Tidak Dikenal!", text_color="red")
            
        # Kembalikan tulisan ke "Silakan Tap Kartu" setelah 3 detik
        self.after(3000, lambda: self.label_status.configure(text="Silakan Tap Kartu Anda...", text_color="white"))


# =====================================================================
# TITIK JALAN APLIKASI
# =====================================================================
if __name__ == "__main__":
    # Menyiapkan tema CustomTkinter
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # Menjalankan mesin utama
    app = MesinPresensiApp()
    app.mainloop()