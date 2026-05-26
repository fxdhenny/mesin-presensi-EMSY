# app/ui/screens.py
import os
import sys
import sqlite3
import customtkinter as ctk
from datetime import datetime

# Konfigurasi jalur database (naik 3 tingkat dari folder ui)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import queries
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'attendance.db')

# =====================================================================
# KONFIGURASI WARNA (Gabungan dari desain UI teman)
# =====================================================================
C = {
    "bg": "#fdfdfc",             # Background utama
    "primary": "#6c5b4b",        # Cokelat Tua 
    "btn": "#b0957b",            # Cokelat Muda (Tombol)
    "btn_hover": "#967e67",      # Hover tombol
    "text": "white",             # Teks putih
    "text_dark": "#6E5A4E",      # Teks gelap untuk welcome
    "top_bar": "#B99B7E",        # Header bar welcome
    "white": "white"
}

# =====================================================================
# LAYAR 1: WELCOME SCREEN (800x480 Optimized)
# =====================================================================
class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        # Header bar atas
        self.top_bar = ctk.CTkFrame(self, height=55, fg_color=C["top_bar"], corner_radius=0)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False) 

        self.label_tanggal = ctk.CTkLabel(self.top_bar, text="", text_color=C["white"], font=("Arial", 16, "bold"))
        self.label_tanggal.pack(side="left", padx=30, pady=10)

        self.label_jam = ctk.CTkLabel(self.top_bar, text="", text_color=C["white"], font=("Arial", 16, "bold"))
        self.label_jam.pack(side="right", padx=30, pady=10)

        self.update_waktu()

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True)

        # WELCOME Besar (Poppins 83 dari kode teman)
        self.label_welcome = ctk.CTkLabel(self.center_frame, text="WELCOME", text_color=C["text_dark"], font=("Poppins", 83, "bold"))
        self.label_welcome.pack(pady=(0, 15))

        # Kotak scan berbentuk Kapsul (Desain teman)
        kapsul_height = 38
        self.box_scan = ctk.CTkFrame(
            self.center_frame, 
            width=240, height=kapsul_height, 
            corner_radius=kapsul_height // 2, 
            border_width=2, border_color=C["text_dark"], fg_color=C["bg"]
        )
        self.box_scan.pack(pady=5)
        self.box_scan.pack_propagate(False)

        self.label_scan = ctk.CTkLabel(self.box_scan, text="Please scan your Rfid!", text_color="black", font=("Arial", 14, "normal"))
        self.label_scan.place(relx=0.5, rely=0.5, anchor="center")

        # Tombol Demo (Tetap dipertahankan untuk testing fungsionalitas)
        self.demo_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.demo_frame.pack(pady=(35, 0))

        self.btn_demo_rombel = ctk.CTkButton(self.demo_frame, text="TAP — KARTU ROMBEL", fg_color=C["btn"], hover_color=C["btn_hover"], text_color=C["white"], font=("Arial", 11, "bold"), corner_radius=14, height=38, command=lambda: master.proses_login("702964954886"))
        self.btn_demo_rombel.pack(side="left", padx=6)

        self.btn_demo_master = ctk.CTkButton(self.demo_frame, text="TAP — KARTU MASTER", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 11, "bold"), corner_radius=14, height=38, command=lambda: master.proses_login("290744317040"))
        self.btn_demo_master.pack(side="left", padx=6)

    def update_waktu(self):
        sekarang = datetime.now()
        # Menggunakan format tanggal sesuai desain teman (contoh: 21 May 2026)
        self.label_tanggal.configure(text=sekarang.strftime("%d %B %Y"))
        self.label_jam.configure(text=sekarang.strftime("%H:%M:%S"))
        self.after(1000, self.update_waktu)

    def ubah_status_scan(self, pesan, warna):
        self.box_scan.configure(border_color=warna)
        self.label_scan.configure(text=pesan, text_color=warna)

    def reset_status_scan(self):
        self.box_scan.configure(border_color=C["text_dark"])
        self.label_scan.configure(text="Please scan your Rfid!", text_color="black")


# =====================================================================
# LAYAR 2: LIST ROMBEL (800x480 Optimized)
# =====================================================================
class RombelSelectScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        # Sidebar Kiri Coklat Tua
        self.sidebar = ctk.CTkFrame(self, width=120, fg_color=C["primary"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="R\nO\nM\nB\nE\nL", text_color=C["text"], font=("Arial", 40, "bold"))
        self.label_sidebar.pack(expand=True)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True)

        # Layout Tombol Grid & Export
        self.grid_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.grid_frame.pack(expand=True, pady=20)

        self.btn_export = ctk.CTkButton(self.grid_frame, text="EXPORT", 
                                        fg_color=C["primary"], hover_color="#5a4c3e", 
                                        text_color=C["text"], font=("Arial", 14, "bold"), 
                                        corner_radius=10, width=120, height=40, 
                                        command=self.eksekusi_export_asli)
        self.btn_export.grid(row=0, column=3, padx=(30, 15), pady=15)

        daftar_rombel = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
        
        for index, rombel in enumerate(daftar_rombel):
            baris = index // 3
            kolom = index % 3
            btn = ctk.CTkButton(self.grid_frame, text=rombel, fg_color=C["btn"], hover_color=C["btn_hover"], text_color=C["text"], font=("Arial", 32, "bold"), width=110, height=90, corner_radius=15, command=lambda r=rombel: self.fungsi_navigasi("nim-list", r))
            btn.grid(row=baris, column=kolom, padx=15, pady=15)

        self.btn_home = ctk.CTkButton(self.main_area, text="← HOME", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 13, "bold"), corner_radius=40, width=90, height=35, command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.place(x=20, y=420)

    def eksekusi_export_asli(self):
        self.btn_export.configure(text="Mengekspor...", fg_color=C["btn"], state="disabled")
        self.update() 
        
        sukses, pesan = queries.export_to_flashdisk(DB_PATH)
        
        if sukses:
            self.btn_export.configure(text="SUKSES!", fg_color="green")
            print(f"[+] {pesan}")
        else:
            self.btn_export.configure(text="GAGAL!", fg_color="red")
            print(f"[-] {pesan}")
            
        self.after(3000, lambda: self.btn_export.configure(text="EXPORT", fg_color=C["primary"], state="normal"))


# =====================================================================
# LAYAR 3: NIM ANGGOTA ROMBEL (Tanpa Scroll)
# =====================================================================
# =====================================================================
# LAYAR 3: NIM ANGGOTA ROMBEL (Tanpa Scroll)
# =====================================================================
class NimListScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.rombel_aktif = ""
        
        # Header Coklat Tua
        self.header = ctk.CTkFrame(self, height=90, fg_color=C["primary"], corner_radius=0)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=40, pady=(0, 30))
        
        # Buat objek tombol Back (Jangan langsung di-.place() di sini agar tidak langsung muncul)
        self.btn_back = ctk.CTkButton(
            self.header, text="< Back", width=70, height=35, 
            fg_color=C["btn"], hover_color=C["btn_hover"], 
            font=("Arial", 14, "bold"), 
            command=lambda: self.fungsi_navigasi("rombel-select")
        )

        self.btn_home = ctk.CTkButton(self.bottom_frame, text="← HOME", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 13, "bold"), corner_radius=40, width=90, height=35, command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.pack(side="left")

        self.label_judul = ctk.CTkLabel(self.header, text='ROMBEL "C3"', text_color=C["text"], font=("Arial", 45, "bold"))
        self.label_judul.pack(expand=True)
        
        # Grid area
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(expand=True, pady=10)

    def update_data(self, string_rombel):
        self.rombel_aktif = string_rombel
        self.label_judul.configure(text=f'ROMBEL "{string_rombel}"')
        
        # --- LOGIKA KENDALI TOMBOL BACK (MASTER VS ROMBEL) ---
        # Mengecek variabel 'is_master' yang ada di kelas utama main.py
        if hasattr(self.master, 'is_master') and self.master.is_master:
            self.btn_back.place(x=20, y=25)  # Munculkan jika akses Master
        else:
            self.btn_back.place_forget()     # Sembunyikan total jika akses Rombel Biasa
        
        kelas_mhs = string_rombel[0]
        rombel_mhs = string_rombel[1:]
        
        queries.inisialisasi_presensi(DB_PATH, kelas_mhs, rombel_mhs)
        data_mhs = queries.ambil_data_presensi_hari_ini(DB_PATH, kelas_mhs, rombel_mhs)
        
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        id_list_rombel = [baris[0] for baris in data_mhs]
        
        # Cetak Grid 4x3
        for index, baris in enumerate(data_mhs):
            id_db = baris[0]
            nim_mahasiswa = baris[2]
            
            baris_grid = index // 3
            kolom_grid = index % 3
            
            btn_nim = ctk.CTkButton(self.grid_frame, text=nim_mahasiswa, fg_color=C["btn"], hover_color=C["btn_hover"], text_color=C["text"], font=("Arial", 22, "bold"), width=200, height=50, corner_radius=25, command=lambda lista=id_list_rombel, idx=index: self.fungsi_navigasi("student-detail", (lista, idx)))
            btn_nim.grid(row=baris_grid, column=kolom_grid, padx=15, pady=10)


# =====================================================================
# LAYAR 4: DATA MAHASISWA 
# =====================================================================
class StudentDetailScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.id_list = []
        self.current_index = 0
        
        # --- FRAME ATAS (Kiri: Info, Kanan: Tombol Bulat) ---
        self.top_section = ctk.CTkFrame(self, fg_color="transparent")
        self.top_section.pack(fill="both", expand=True, padx=40, pady=(30, 30))

        self.top_frame = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.left_frame = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=(5, 0))
        

        self.title_label = ctk.CTkLabel(self.top_frame, text="DATA MAHASISWA", text_color=C["primary"], font=("Arial", 45, "bold"), justify="left")
        self.title_label.pack(anchor="center", pady=(0, 20))
        
        # Panel Info
        self.card_info = ctk.CTkFrame(self.left_frame, fg_color=C["btn"], corner_radius=15, height=250)
        self.card_info.pack(fill="x")
        self.card_info.pack_propagate(False)
        
        self.label_nama = ctk.CTkLabel(self.card_info, text="Nama : ", text_color=C["white"], font=("Arial", 22, "bold"), wraplength=350, justify="left")
        self.label_nama.pack(anchor="w", padx=20, pady=(40, 10))
        
        self.label_nim = ctk.CTkLabel(self.card_info, text="NIM    : ", text_color=C["white"], font=("Arial", 22, "bold"))
        self.label_nim.pack(anchor="w", padx=20, pady=4)
        
        self.label_kelas = ctk.CTkLabel(self.card_info, text="Kelas  : ", text_color=C["white"], font=("Arial", 22, "bold"))
        self.label_kelas.pack(anchor="w", padx=20, pady=4)

        self.label_status_info = ctk.CTkLabel(self.card_info, text="Status  : ", text_color=C["white"], font=("Arial", 22, "bold"))
        self.label_status_info.pack(anchor="w", padx=20, pady=4)

        # --- Bagian Kanan (Tombol Presensi) ---
        self.right_frame = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.right_frame.pack(side="right", fill="y", padx=(0, 0), pady=(0, 0))
        
        # Labeling baru disesuaikan dengan kode teman
        self.opsi_bulatan = [
            {"label": " I ", "kolom": "status", "nilai": "izin", "warna_aktif": "#1d4e89"},
            {"label": " S ", "kolom": "status", "nilai": "sakit", "warna_aktif": "#92400e"},
            {"label": "HT", "kolom": "kedatangan", "nilai": "tepat waktu", "warna_aktif": "#064e3b"},
            {"label": "TL", "kolom": "kedatangan", "nilai": "terlambat", "warna_aktif": "#78350f"},
            {"label": "PT", "kolom": "kepulangan", "nilai": "tepat waktu", "warna_aktif": "#064e3b"},
            {"label": "PC", "kolom": "kepulangan", "nilai": "lebih awal", "warna_aktif": "#78350f"}
        ]
        
        self.tombol_bulat_list = []
        for index, item in enumerate(self.opsi_bulatan):
            baris = index // 2
            kolom = index % 2
            ukuran = 70  # Lingkaran sempurna sesuai kode teman
            
            btn_bulat = ctk.CTkButton(self.right_frame, text=item["label"], font=("Arial", 26, "bold"), text_color=C["white"], fg_color=C["btn"], hover_color=C["btn_hover"], width=ukuran, height=ukuran, corner_radius=ukuran // 2, command=lambda k=item["kolom"], n=item["nilai"]: self.proses_presensi_visual(k, n))
            btn_bulat.grid(row=baris, column=kolom, padx=8, pady=8)
            self.tombol_bulat_list.append(btn_bulat)

        # --- FRAME BAWAH (Navigasi) ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=40, pady=(0, 30))
        
        self.btn_back = ctk.CTkButton(self.bottom_frame, text="< BACK", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 20, "bold"), corner_radius=25, width=140, height=50, command=lambda: self.fungsi_navigasi("nim-list"))
        self.btn_back.pack(side="left")
        
        self.btn_home = ctk.CTkButton(self.bottom_frame, text="HOME", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 20, "bold"), corner_radius=25, width=140, height=50, command=lambda: self.fungsi_navigasi("welcome"))
        self.btn_home.place(relx=0.5, rely=0.5, anchor="center")
        
        self.btn_next = ctk.CTkButton(self.bottom_frame, text="NEXT >", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 20, "bold"), corner_radius=25, width=140, height=50, command=self.geser_mahasiswa_next)
        self.btn_next.pack(side="right")

    def update_data(self, data_tuple):
        if data_tuple == "kembali":
            return
        self.id_list, self.current_index = data_tuple
        self.refresh_profil_mahasiswa()
        
    def refresh_profil_mahasiswa(self):
        id_db_sekarang = self.id_list[self.current_index]
        
        if self.current_index == len(self.id_list) - 1:
            self.btn_next.configure(state="disabled", fg_color=C["btn"])
        else:
            self.btn_next.configure(state="normal", fg_color=C["primary"])
            
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
                
                self.label_nama.configure(text=f"Nama :  {nama}")
                self.label_nim.configure(text=f"NIM    :  {nim}")
                self.label_kelas.configure(text=f"Kelas  :  {kelas}")
                
                if status == "hadir":
                    str_datang = datang.title() if datang else "-"
                    str_pulang = pulang.title() if pulang else "-"
                    teks_status = f"Status  :  Hadir ({str_datang} | {str_pulang})"
                else:
                    teks_status = f"Status  :  {status.title()}"
                    
                self.label_status_info.configure(text=teks_status)
                
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
                        self.tombol_bulat_list[index].configure(fg_color=C["btn"])
                        
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