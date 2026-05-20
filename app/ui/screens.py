import os
import sys

# Trik Engineer: Menambahkan path root agar file screens.py bisa memanggil database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import queries

# Definisi jalur database (naik 3 tingkat dari lokasi file ini)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'attendance.db')

# app/ui/screens.py
import customtkinter as ctk
from datetime import datetime
from ui.colors import C

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        self.top_bar = ctk.CTkFrame(self, height=50, fg_color=C["tan"], corner_radius=0)
        self.top_bar.pack(side="top", fill="x")

        self.label_tanggal = ctk.CTkLabel(self.top_bar, text="", text_color=C["white"], font=("Helvetica", 18, "bold"))
        self.label_tanggal.pack(side="left", padx=32, pady=10)

        self.label_jam = ctk.CTkLabel(self.top_bar, text="", text_color=C["white"], font=("Helvetica", 18, "bold"))
        self.label_jam.pack(side="right", padx=32, pady=10)

        self.update_waktu()

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True)

        self.label_welcome = ctk.CTkLabel(self.center_frame, text="WELCOME", text_color=C["dark"], font=("Helvetica", 90, "bold"))
        self.label_welcome.pack(pady=(0, 20))

        self.box_scan = ctk.CTkFrame(self.center_frame, fg_color="transparent", border_width=3, border_color=C["darker"], corner_radius=40)
        self.box_scan.pack(pady=10, ipadx=20, ipady=5)

        self.label_scan = ctk.CTkLabel(self.box_scan, text="Please scan your Rfid!", text_color=C["darker"], font=("Helvetica", 20, "bold"))
        self.label_scan.pack(padx=28, pady=14)

        self.demo_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.demo_frame.pack(pady=(30, 0))

        self.btn_demo_rombel = ctk.CTkButton(self.demo_frame, text="TAP — KARTU ROMBEL", fg_color=C["tan"], hover_color=C["tanDark"], text_color=C["white"], font=("Helvetica", 14, "bold"), corner_radius=14, height=45, command=lambda: master.proses_login("702964954886"))
        self.btn_demo_rombel.pack(side="left", padx=8)

        self.btn_demo_master = ctk.CTkButton(self.demo_frame, text="TAP — KARTU MASTER", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Helvetica", 14, "bold"), corner_radius=14, height=45, command=lambda: master.proses_login("290744317040"))
        self.btn_demo_master.pack(side="left", padx=8)

    def update_waktu(self):
        sekarang = datetime.now()
        hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][sekarang.weekday()]
        bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agt", "Sep", "Okt", "Nov", "Des"][sekarang.month - 1]
        self.label_tanggal.configure(text=f"{hari}, {sekarang.day} {bulan} {sekarang.year}")
        self.label_jam.configure(text=sekarang.strftime("%H:%M:%S"))
        self.after(1000, self.update_waktu)

    def ubah_status_scan(self, pesan, warna):
        self.box_scan.configure(border_color=warna)
        self.label_scan.configure(text=pesan, text_color=warna)

    def reset_status_scan(self):
        self.box_scan.configure(border_color=C["darker"])
        self.label_scan.configure(text="Please scan your Rfid!", text_color=C["darker"])


class RombelSelectScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        self.sidebar = ctk.CTkFrame(self, width=80, fg_color=C["dark"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        teks_vertikal = "R\nO\nM\nB\nE\nL"
        self.label_sidebar = ctk.CTkLabel(self.sidebar, text=teks_vertikal, text_color=C["white"], font=("Helvetica", 24, "bold"))
        self.label_sidebar.pack(expand=True)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True, padx=40, pady=40)

        self.btn_export = ctk.CTkButton(self.main_area, text="EXPORT", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Helvetica", 16, "bold"), corner_radius=14, width=120, height=40, command=self.simulasi_export)
        self.btn_export.pack(side="top", anchor="ne", pady=(0, 20))

        self.grid_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.grid_frame.pack(expand=True)

        DAFTAR_ROMBEL = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
        
        for index, rombel in enumerate(DAFTAR_ROMBEL):
            baris = index // 3  
            kolom = index % 3   

            btn = ctk.CTkButton(self.grid_frame, text=rombel, fg_color=C["tan"], hover_color=C["tanLight"], text_color=C["white"], font=("Helvetica", 38, "bold"), width=110, height=110, corner_radius=20, command=lambda r=rombel: self.fungsi_navigasi("nim-list", r))
            btn.grid(row=baris, column=kolom, padx=15, pady=15)

        self.btn_home = ctk.CTkButton(self.main_area, text="← HOME", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Helvetica", 14, "bold"), corner_radius=40, width=100, height=40, command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.pack(side="bottom", anchor="sw")

    def simulasi_export(self):
        self.btn_export.configure(text="Mengekspor...", fg_color=C["tanDark"], state="disabled")
        self.after(1800, self.export_selesai)
        
    def export_selesai(self):
        self.btn_export.configure(text="SUKSES!", fg_color="green")
        self.after(2000, lambda: self.btn_export.configure(text="EXPORT", fg_color=C["dark"], state="normal"))

# =====================================================================
# 4. KOMPONEN LAYAR 3: NIM LIST (Daftar Mahasiswa per Rombel)
# =====================================================================
class NimListScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.rombel_aktif = ""
        
        # --- HEADER GELAP ---
        self.header = ctk.CTkFrame(self, fg_color=C["dark"], corner_radius=0)
        self.header.pack(side="top", fill="x")
        
        self.label_judul = ctk.CTkLabel(self.header, text="ROMBEL", 
                                        text_color=C["white"], font=("Helvetica", 36, "bold"))
        self.label_judul.pack(pady=22)
        
        # --- AREA SCROLL UNTUK TOMBOL NIM ---
        # Menggunakan ScrollableFrame agar bisa digeser jika mahasiswa lebih dari belasan
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Frame penampung grid di dalam area scroll
        self.grid_frame = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
        self.grid_frame.pack(expand=True)
        
        # --- NAVIGASI BAWAH ---
        self.nav_bawah = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_bawah.pack(side="bottom", fill="x", padx=40, pady=(0, 32))
        
        self.btn_back = ctk.CTkButton(self.nav_bawah, text="‹ BACK", 
                                      fg_color=C["dark"], hover_color=C["darker"], 
                                      text_color=C["white"], font=("Helvetica", 16, "bold"), 
                                      corner_radius=40, width=120, height=45, 
                                      command=lambda: self.fungsi_navigasi("rombel-select"))
        self.btn_back.pack(side="left")
        
        self.btn_home = ctk.CTkButton(self.nav_bawah, text="HOME", 
                                      fg_color=C["dark"], hover_color=C["darker"], 
                                      text_color=C["white"], font=("Helvetica", 16, "bold"), 
                                      corner_radius=40, width=120, height=45, 
                                      command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.pack(side="right")

    def update_data(self, string_rombel):
        """
        Fungsi ajaib yang dipanggil otomatis oleh main.py saat halaman ini mau dibuka.
        Tugasnya: Menarik data SQLite, lalu mencetak tombol-tombol NIM.
        """
        self.rombel_aktif = string_rombel
        self.label_judul.configure(text=f'ROMBEL "{string_rombel}"')
        
        # Memecah string "A1" menjadi kelas "A" dan rombel "1"
        kelas_mhs = string_rombel[0]
        rombel_mhs = string_rombel[1:]
        
        # 1. Pastikan absensi hari ini sudah dibuat (Sama seperti logika CLI)
        queries.inisialisasi_presensi(DB_PATH, kelas_mhs, rombel_mhs)
        
        # 2. Tarik data dari database
        data_mhs = queries.ambil_data_presensi_hari_ini(DB_PATH, kelas_mhs, rombel_mhs)
        
        # 3. Hancurkan/Bersihkan tombol-tombol bekas rombel sebelumnya (jika ada)
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        # 4. Cetak ulang tombol NIM baru berdasarkan data database (Grid 3 Kolom)
        for index, baris in enumerate(data_mhs):
            # Format baris dari queries.py: (id_db, no_absen, nim, nama, status, datang, pulang)
            id_db = baris[0]
            nim_mahasiswa = baris[2]
            
            baris_grid = index // 3
            kolom_grid = index % 3
            
            btn_nim = ctk.CTkButton(self.grid_frame, text=nim_mahasiswa,
                                    fg_color=C["tan"], hover_color=C["tanLight"],
                                    text_color=C["white"], font=("Helvetica", 18, "bold"),
                                    width=150, height=70, corner_radius=16,
                                    # Mengirim id_db database ke layar ke-4 (Student Detail)
                                    command=lambda db_id=id_db: self.fungsi_navigasi("student-detail", db_id))
            btn_nim.grid(row=baris_grid, column=kolom_grid, padx=10, pady=10)

# =====================================================================
# 5. KOMPONEN LAYAR 4: STUDENT DETAIL (Ubah Absensi)
# =====================================================================
class StudentDetailScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.id_db_aktif = None
        
        # --- HEADER (Data Diri) ---
        self.header_frame = ctk.CTkFrame(self, fg_color=C["tan"], corner_radius=20)
        self.header_frame.pack(fill="x", padx=40, pady=(30, 20), ipadx=20, ipady=20)
        
        self.label_nama = ctk.CTkLabel(self.header_frame, text="NAMA MAHASISWA", 
                                       text_color=C["white"], font=("Helvetica", 28, "bold"))
        self.label_nama.pack(anchor="w")
        
        self.label_nim = ctk.CTkLabel(self.header_frame, text="NIM: -", 
                                      text_color=C["white"], font=("Helvetica", 18))
        self.label_nim.pack(anchor="w", pady=(5, 0))

        # Status Terkini (Hadir/Alfa, Datang, Pulang)
        self.status_bar = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.status_bar.pack(anchor="w", pady=(10, 0))
        
        self.badge_status = ctk.CTkLabel(self.status_bar, text="STATUS: -", fg_color=C["dark"], 
                                         text_color=C["white"], font=("Helvetica", 14, "bold"), corner_radius=10, width=120)
        self.badge_status.pack(side="left", padx=(0, 10))
        
        self.badge_datang = ctk.CTkLabel(self.status_bar, text="DTG: -", fg_color=C["dark"], 
                                         text_color=C["white"], font=("Helvetica", 14, "bold"), corner_radius=10, width=150)
        self.badge_datang.pack(side="left", padx=(0, 10))

        self.badge_pulang = ctk.CTkLabel(self.status_bar, text="PLG: -", fg_color=C["dark"], 
                                         text_color=C["white"], font=("Helvetica", 14, "bold"), corner_radius=10, width=150)
        self.badge_pulang.pack(side="left")

        # --- TOMBOL AKSI (Grid 2x3) ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(expand=True)
        
        # Opsi yang mereplikasi Dial CLI Anda sebelumnya
        opsi_status = [
            ("HADIR", "status", "hadir"),
            ("IZIN", "status", "izin"),
            ("SAKIT", "status", "sakit"),
            ("ALFA", "status", "alfa"),
            ("DTG: TEPAT", "kedatangan", "tepat waktu"),
            ("DTG: TELAT", "kedatangan", "terlambat"),
            ("PLG: TEPAT", "kepulangan", "tepat waktu"),
            ("PLG: CEPAT", "kepulangan", "lebih awal"),
            ("HAPUS DTG/PLG", "reset", "reset") # Tombol ekstra untuk Poka-Yoke manual
        ]
        
        for index, (label_teks, kolom, nilai) in enumerate(opsi_status):
            baris = index // 3
            kolom_grid = index % 3
            
            btn = ctk.CTkButton(self.action_frame, text=label_teks,
                                fg_color=C["tanDark"], hover_color=C["dark"],
                                text_color=C["white"], font=("Helvetica", 16, "bold"),
                                width=140, height=70, corner_radius=35,
                                command=lambda k=kolom, n=nilai: self.eksekusi_ubah_data(k, n))
            btn.grid(row=baris, column=kolom_grid, padx=15, pady=15)

        # --- NAVIGASI BAWAH ---
        self.nav_bawah = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_bawah.pack(side="bottom", fill="x", padx=40, pady=(0, 32))
        
        # Tombol BACK (Akan membawa data rombel_aktif kembali ke layar NIM List)
        self.btn_back = ctk.CTkButton(self.nav_bawah, text="‹ BACK", 
                                      fg_color=C["dark"], hover_color=C["darker"], 
                                      text_color=C["white"], font=("Helvetica", 16, "bold"), 
                                      corner_radius=40, width=120, height=45, 
                                      command=self.kembali_ke_nim_list)
        self.btn_back.pack(side="left")

    def update_data(self, id_db):
        """Dipanggil oleh main.py saat tombol NIM diklik. Menerima ID Database mahasiswa."""
        self.id_db_aktif = id_db
        self.refresh_tampilan()
        
    def refresh_tampilan(self):
        """Menarik data individu dari SQLite dan menampilkannya ke layar"""
        if not self.id_db_aktif: return
        
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Query khusus untuk menarik data 1 orang saja berdasarkan ID presensi
            cursor.execute('''
                SELECT m.nama, m.nim, p.status, p.kedatangan, p.kepulangan, m.target_kelas, m.target_rombel
                FROM presensi_harian p
                JOIN mahasiswa m ON p.mahasiswa_id = m.id
                WHERE p.id = ?
            ''', (self.id_db_aktif,))
            
            hasil = cursor.fetchone()
            conn.close()
            
            if hasil:
                nama, nim, status, datang, pulang, kelas, rombel = hasil
                # Simpan asal rombel mahasiswa ini untuk keperluan tombol Back
                self.asal_rombel = f"{kelas}{rombel}" 
                
                self.label_nama.configure(text=nama.upper())
                self.label_nim.configure(text=f"NIM: {nim}")
                
                self.badge_status.configure(text=f"STATUS: {str(status).upper()}")
                self.badge_datang.configure(text=f"DTG: {str(datang).upper() if datang else '-'}")
                self.badge_pulang.configure(text=f"PLG: {str(pulang).upper() if pulang else '-'}")
                
        except Exception as e:
            print(f"[-] Kesalahan baca data individu: {e}")

    def eksekusi_ubah_data(self, kolom, nilai):
        """Mengeksekusi query database berdasarkan tombol yang diklik"""
        if not self.id_db_aktif: return
        
        # Logika Khusus: Poka-Yoke (Hapus jam datang/pulang jika diset Alfa/Izin/Sakit)
        if kolom == "status" and nilai in ['alfa', 'izin', 'sakit']:
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, 'status', nilai)
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, 'kedatangan', None)
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, 'kepulangan', None)
            
        # Logika Khusus: Poka-Yoke (Paksa Hadir jika jam datang/pulang diisi)
        elif kolom in ["kedatangan", "kepulangan"]:
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, kolom, nilai)
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, 'status', 'hadir')
            
        # Tombol ekstra untuk menghapus data jam
        elif kolom == "reset":
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, 'kedatangan', None)
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, 'kepulangan', None)
            
        # Perubahan status normal (Hadir)
        else:
            queries.update_status_presensi(DB_PATH, self.id_db_aktif, kolom, nilai)
            
        # Segarkan layar untuk melihat efek perubahannya secara instan!
        self.refresh_tampilan()
        
    def kembali_ke_nim_list(self):
        """Tombol back harus mengirimkan ulang data rombel agar layar NIM List mencetak tombol kembali"""
        if hasattr(self, 'asal_rombel'):
            self.fungsi_navigasi("nim-list", self.asal_rombel)