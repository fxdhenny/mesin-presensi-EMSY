# app/ui/screens.py
import os
import sys
import sqlite3
import customtkinter as ctk
from datetime import datetime

# Mengimpor palet warna tunggal
from ui.colors import C

# Konfigurasi jalur database (naik 3 tingkat dari folder ui)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import queries
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'attendance.db')


# =====================================================================
# LAYAR 1: WELCOME SCREEN (800x480 Optimized)
# =====================================================================
class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        # Header bar atas
        self.top_bar = ctk.CTkFrame(self, height=45, fg_color=C["tan"], corner_radius=0)
        self.top_bar.pack(side="top", fill="x")

        self.label_tanggal = ctk.CTkLabel(self.top_bar, text="", text_color=C["white"], font=("Nunito", 16, "bold"))
        self.label_tanggal.pack(side="left", padx=25, pady=8)

        self.label_jam = ctk.CTkLabel(self.top_bar, text="", text_color=C["white"], font=("Nunito", 16, "bold"))
        self.label_jam.pack(side="right", padx=25, pady=8)

        self.update_waktu()

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True)

        # WELCOME Besar sesuai Gambar 1
        self.label_welcome = ctk.CTkLabel(self.center_frame, text="WELCOME", text_color=C["dark"], font=("Nunito", 90, "bold"))
        self.label_welcome.pack(pady=(0, 20))

        # Kotak scan melingkar
        self.box_scan = ctk.CTkFrame(self.center_frame, fg_color="transparent", border_width=2.5, border_color=C["darker"], corner_radius=40)
        self.box_scan.pack(pady=10, ipadx=20, ipady=5)

        self.label_scan = ctk.CTkLabel(self.box_scan, text="Please scan your Rfid!", text_color=C["darker"], font=("Nunito", 18, "bold"))
        self.label_scan.pack(padx=24, pady=12)

        # Tombol Demo Tap
        self.demo_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.demo_frame.pack(pady=(25, 0))

        self.btn_demo_rombel = ctk.CTkButton(self.demo_frame, text="TAP — KARTU ROMBEL", fg_color=C["tan"], hover_color=C["tanDark"], text_color=C["white"], font=("Nunito", 11, "bold"), corner_radius=14, height=38, command=lambda: master.proses_login("702964954886"))
        self.btn_demo_rombel.pack(side="left", padx=6)

        self.btn_demo_master = ctk.CTkButton(self.demo_frame, text="TAP — KARTU MASTER", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Nunito", 11, "bold"), corner_radius=14, height=38, command=lambda: master.proses_login("290744317040"))
        self.btn_demo_master.pack(side="left", padx=6)

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


# =====================================================================
# LAYAR 2: LIST ROMBEL (800x480 Optimized)
# =====================================================================
class RombelSelectScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        # Sidebar Kiri Coklat Gelap sesuai Gambar 2
        self.sidebar = ctk.CTkFrame(self, width=70, fg_color=C["dark"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="R\nO\nM\nB\nE\nL", text_color=C["white"], font=("Nunito", 24, "bold"))
        self.label_sidebar.pack(expand=True)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True, padx=25, pady=25)

        # Tombol EXPORT Kanan Atas
        self.btn_export = ctk.CTkButton(self.main_area, text="EXPORT", 
                                        fg_color=C["dark"], hover_color=C["darker"], 
                                        text_color=C["white"], font=("Nunito", 15, "bold"), 
                                        corner_radius=14, width=110, height=38, 
                                        command=self.eksekusi_export_asli)

        self.grid_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.grid_frame.pack(expand=True)

        daftar_rombel = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
        
        for index, rombel in enumerate(daftar_rombel):
            baris = index // 3
            kolom = index % 3
            btn = ctk.CTkButton(self.grid_frame, text=rombel, fg_color=C["tan"], hover_color=C["tanLight"], text_color=C["white"], font=("Nunito", 32, "bold"), width=105, height=105, corner_radius=18, command=lambda r=rombel: self.fungsi_navigasi("nim-list", r))
            btn.grid(row=baris, column=kolom, padx=12, pady=12)

        self.btn_home = ctk.CTkButton(self.main_area, text="← HOME", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Nunito", 13, "bold"), corner_radius=40, width=90, height=35, command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.pack(side="bottom", anchor="sw")

    # PERBAIKAN: Fungsi ini kini digeser sejajar dengan def __init__
    def eksekusi_export_asli(self):
        """Memanggil fungsi export SQLite ke CSV di Flashdisk"""
        self.btn_export.configure(text="Mengekspor...", fg_color=C["tanDark"], state="disabled")
        self.update() 
        
        sukses, pesan = queries.export_to_flashdisk(DB_PATH)
        
        if sukses:
            self.btn_export.configure(text="SUKSES!", fg_color="green")
            print(f"[+] {pesan}")
        else:
            self.btn_export.configure(text="GAGAL!", fg_color="red")
            print(f"[-] {pesan}")
            
        self.after(3000, lambda: self.btn_export.configure(text="EXPORT", fg_color=C["dark"], state="normal"))


# =====================================================================
# LAYAR 3: NIM ANGGOTA ROMBEL (Tanpa Scroll - Gambar 3 Match)
# =====================================================================
class NimListScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.rombel_aktif = ""
        
        # Header Coklat Gelap sesuai Gambar 3
        self.header = ctk.CTkFrame(self, height=65, fg_color=C["dark"], corner_radius=0)
        self.header.pack(side="top", fill="x")
        
        self.label_judul = ctk.CTkLabel(self.header, text='ROMBEL "C3"', text_color=C["white"], font=("Nunito", 36, "bold"))
        self.label_judul.pack(pady=12)
        
        # Frame Konten Utama Tanpa Scrollbar agar 100% Fit di Waveshare
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(expand=True, padx=30, pady=15)
        
        # Navigasi Bawah
        self.nav_bawah = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_bawah.pack(side="bottom", fill="x", padx=45, pady=(0, 25))
        
        self.btn_back = ctk.CTkButton(self.nav_bawah, text="‹ BACK", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Nunito", 14, "bold"), corner_radius=40, width=110, height=40, command=lambda: self.fungsi_navigasi("rombel-select"))
        self.btn_back.pack(side="left")
        
        self.btn_home = ctk.CTkButton(self.nav_bawah, text="HOME", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Nunito", 14, "bold"), corner_radius=40, width=110, height=40, command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.pack(side="right")

    def update_data(self, string_rombel):
        """Menarik data 12 anak dan merendernya ke susunan 3x4 Grid secara pas"""
        self.rombel_aktif = string_rombel
        self.label_judul.configure(text=f'ROMBEL "{string_rombel}"')
        
        kelas_mhs = string_rombel[0]
        rombel_mhs = string_rombel[1:]
        
        queries.inisialisasi_presensi(DB_PATH, kelas_mhs, rombel_mhs)
        data_mhs = queries.ambil_data_presensi_hari_ini(DB_PATH, kelas_mhs, rombel_mhs)
        
        # Bersihkan tombol lama
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        # Simpan seluruh ID presensi di rombel ini agar bisa dioper ke tombol NEXT di Layar 4
        id_list_rombel = [baris[0] for baris in data_mhs]
        
        # Cetak Grid 4 Baris x 3 Kolom persis seperti Gambar 3
        for index, baris in enumerate(data_mhs):
            id_db = baris[0]
            nim_mahasiswa = baris[2]
            
            baris_grid = index // 3
            kolom_grid = index % 3
            
            # Dimensi tombol dihitung ketat agar tidak memicu overflow/scroll di layar 480px
            btn_nim = ctk.CTkButton(self.grid_frame, text=nim_mahasiswa, fg_color=C["tan"], hover_color=C["tanLight"], text_color=C["white"], font=("Nunito", 18, "bold"), width=210, height=52, corner_radius=16, command=lambda lista=id_list_rombel, idx=index: self.fungsi_navigasi("student-detail", (lista, idx)))
            btn_nim.grid(row=baris_grid, column=kolom_grid, padx=15, pady=8)


# =====================================================================
# LAYAR 4: DATA MAHASISWA (Smart Toggle Switch & Auto-Wrap Name)
# =====================================================================
class StudentDetailScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.id_list = []
        self.current_index = 0
        
        # --- JUDUL BESAR KIRI ---
        self.title_label = ctk.CTkLabel(self, text="DATA\nMAHASISWA", text_color=C["dark"], font=("Nunito", 38, "bold"), justify="left")
        self.title_label.place(x=45, y=30)
        
        # --- PANEL INFORMASI COKLAT MUDA ---
        self.card_info = ctk.CTkFrame(self, width=380, height=220, fg_color=C["tan"], corner_radius=20)
        self.card_info.place(x=45, y=140)
        self.card_info.pack_propagate(False)
        
        # MODIFIKASI 1: Ditambahkan wraplength=320 dan justify="left" agar nama panjang otomatis turun ke bawah
        # Ukuran font disesuaikan ke 16 agar ruang vertikal tetap longgar dan aman dari overflow
        self.label_nama = ctk.CTkLabel(self.card_info, text="Nama : ", text_color=C["white"], 
                                          font=("Nunito", 16, "bold"), wraplength=320, justify="left")
        self.label_nama.pack(anchor="w", padx=25, pady=(20, 4))
        
        self.label_nim = ctk.CTkLabel(self.card_info, text="NIM    : ", text_color=C["white"], font=("Nunito", 16, "bold"))
        self.label_nim.pack(anchor="w", padx=25, pady=4)
        
        self.label_kelas = ctk.CTkLabel(self.card_info, text="Kelas  : ", text_color=C["white"], font=("Nunito", 16, "bold"))
        self.label_kelas.pack(anchor="w", padx=25, pady=4)

        # MODIFIKASI 2: Menambahkan Label Keterangan Status tepat di bawah kelas
        self.label_status_info = ctk.CTkLabel(self.card_info, text="Status  : ", text_color=C["white"], font=("Nunito", 16, "bold"))
        self.label_status_info.pack(anchor="w", padx=25, pady=4)

        # --- PANEL BULATAN AKSES 2x3 KANAN ---
        self.grid_bulatan = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_bulatan.place(x=460, y=25)
        
        self.opsi_bulatan = [
            {"label": "I", "kolom": "status", "nilai": "izin", "warna_aktif": "#1d4e89"},
            {"label": "S", "kolom": "status", "nilai": "sakit", "warna_aktif": "#92400e"},
            {"label": "DT", "kolom": "kedatangan", "nilai": "tepat waktu", "warna_aktif": "#064e3b"},
            {"label": "DL", "kolom": "kedatangan", "nilai": "terlambat", "warna_aktif": "#78350f"},
            {"label": "PT", "kolom": "kepulangan", "nilai": "tepat waktu", "warna_aktif": "#064e3b"},
            {"label": "PC", "kolom": "kepulangan", "nilai": "lebih awal", "warna_aktif": "#78350f"}
        ]
        
        self.tombol_bulat_list = []
        for index, item in enumerate(self.opsi_bulatan):
            baris = index // 2
            kolom = index % 2
            
            btn_bulat = ctk.CTkButton(self.grid_bulatan, text=item["label"], font=("Nunito", 28, "bold"), text_color=C["white"], fg_color=C["tan"], hover_color=C["tanLight"], width=82, height=82, corner_radius=41, command=lambda k=item["kolom"], n=item["nilai"]: self.proses_presensi_visual(k, n))
            btn_bulat.grid(row=baris, column=kolom, padx=20, pady=12)
            self.tombol_bulat_list.append(btn_bulat)

        # --- TOMBOL NAVIGASI BAWAH ---
        self.btn_back = ctk.CTkButton(self, text="‹ BACK", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Nunito", 16, "bold"), corner_radius=40, width=150, height=45, command=lambda: self.fungsi_navigasi("nim-list", "kembali"))
        self.btn_back.place(x=45, y=400)
        
        self.btn_home = ctk.CTkButton(self, text="HOME", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Nunito", 16, "bold"), corner_radius=40, width=150, height=45, command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.place(x=325, y=400)
        
        self.btn_next = ctk.CTkButton(self, text="NEXT ›", fg_color=C["dark"], hover_color=C["darker"], text_color=C["white"], font=("Nunito", 16, "bold"), corner_radius=40, width=150, height=45, command=self.geser_mahasiswa_next)
        self.btn_next.place(x=605, y=400)

    def update_data(self, data_tuple):
        if data_tuple == "kembali":
            return
        self.id_list, self.current_index = data_tuple
        self.refresh_profil_mahasiswa()
        
    def refresh_profil_mahasiswa(self):
        id_db_sekarang = self.id_list[self.current_index]
        
        if self.current_index == len(self.id_list) - 1:
            self.btn_next.configure(state="disabled", fg_color=C["tan"])
        else:
            self.btn_next.configure(state="normal", fg_color=C["dark"])
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.nama, m.nim, m.target_kelas, p.status, p.kedatangan, p.kepulangan
                FROM presensi_harian p
                JOIN mahasiswa m ON p.mahasiswa_id = m.id
                WHERE p.id = ?
            ''', (id_db_sekarang,))
            hasil = cursor.fetchone()
            conn.close()
            
            if hasil:
                nama, nim, kelas, status, datang, pulang = hasil
                
                # Menampilkan teks dasar profil
                self.label_nama.configure(text=f"Nama :  {nama}")
                self.label_nim.configure(text=f"NIM    :  {nim}")
                self.label_kelas.configure(text=f"Kelas  :  {kelas}")
                
                # MODIFIKASI 3: Logika Penyusunan Teks Keterangan Status Secara Dinamis
                if status == "hadir":
                    str_datang = datang.title() if datang else "-"
                    str_pulang = pulang.title() if pulang else "-"
                    teks_status = f"Status  :  Hadir ({str_datang} | {str_pulang})"
                else:
                    teks_status = f"Status  :  {status.title()}"
                    
                self.label_status_info.configure(text=teks_status)
                
                # Merender warna bulatan aktif
                for index, item in enumerate(self.opsi_bulatan):
                    is_active = False
                    if item["kolom"] == "status" and status == item["nilai"]:
                        is_active = True
                    elif item["kolom"] == "kedatangan" and datang == item["nilai"]:
                        is_active = True
                    elif item["kolom"] == "kepulangan" and pulang == item["nilai"]:
                        is_active = True
                        
                    if is_active:
                        self.tombol_bulat_list[index].configure(fg_color=item["warna_aktif"])
                    else:
                        self.tombol_bulat_list[index].configure(fg_color=C["tan"])
                        
        except Exception as e:
            print(f"[-] Gagal memuat data detail visual: {e}")

    def proses_presensi_visual(self, kolom, nilai):
        id_db_sekarang = self.id_list[self.current_index]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT status, kedatangan, kepulangan FROM presensi_harian WHERE id = ?", (id_db_sekarang,))
        hasil = cursor.fetchone()
        conn.close()
        
        if not hasil: return
        current_status, current_datang, current_pulang = hasil
        
        if kolom == "status":
            if current_status == nilai:
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'status', 'alfa')
            else:
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'status', nilai)
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'kedatangan', None)
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'kepulangan', None)
                
        elif kolom == "kedatangan":
            if current_datang == nilai:
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'kedatangan', None)
                if not current_pulang:
                    queries.update_status_presensi(DB_PATH, id_db_sekarang, 'status', 'alfa')
            else:
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'kedatangan', nilai)
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'status', 'hadir')
                
        elif kolom == "kepulangan":
            if current_pulang == nilai:
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'kepulangan', None)
                if not current_datang:
                    queries.update_status_presensi(DB_PATH, id_db_sekarang, 'status', 'alfa')
            else:
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'kepulangan', nilai)
                queries.update_status_presensi(DB_PATH, id_db_sekarang, 'status', 'hadir')
                
        self.refresh_profil_mahasiswa()
        
    def geser_mahasiswa_next(self):
        if self.current_index < len(self.id_list) - 1:
            self.current_index += 1
            self.refresh_profil_mahasiswa()