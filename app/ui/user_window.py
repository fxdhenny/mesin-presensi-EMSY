# app/ui/user_window.py
import os
import sys
import sqlite3
import customtkinter as ctk

# Import konfigurasi dan database
from ui.colors import C
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import queries
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'attendance.db')

class NimListScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.rombel_aktif = ""
        
        self.header = ctk.CTkFrame(self, height=90, fg_color=C["primary"], corner_radius=0)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=40, pady=(0, 30))
        
        self.btn_home = ctk.CTkButton(self.bottom_frame, text="< BACK", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 13, "bold"), corner_radius=40, width=90, height=35, command=self.kembali)
        self.btn_home.pack(side="left")

        self.label_judul = ctk.CTkLabel(self.header, text='ROMBEL "C3"', text_color=C["text"], font=("Arial", 45, "bold"))
        self.label_judul.pack(expand=True)
        
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(expand=True, pady=10)

    def update_data(self, string_rombel):
        self.rombel_aktif = string_rombel
        self.label_judul.configure(text=f'ROMBEL "{string_rombel}"')
        
        kelas_mhs = string_rombel[0]
        rombel_mhs = string_rombel[1:]
        
        queries.inisialisasi_presensi(DB_PATH, kelas_mhs, rombel_mhs)
        data_mhs = queries.ambil_data_presensi_hari_ini(DB_PATH, kelas_mhs, rombel_mhs)
        
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        id_list_rombel = [baris[0] for baris in data_mhs]
        
        for index, baris in enumerate(data_mhs):
            id_db = baris[0]
            nim_mahasiswa = baris[2]
            
            baris_grid = index // 3
            kolom_grid = index % 3
            
            btn_nim = ctk.CTkButton(self.grid_frame, text=nim_mahasiswa, fg_color=C["btn"], hover_color=C["btn_hover"], text_color=C["text"], font=("Arial", 22, "bold"), width=200, height=50, corner_radius=25, command=lambda lista=id_list_rombel, idx=index: self.fungsi_navigasi("student-detail", (lista, idx)))
            btn_nim.grid(row=baris_grid, column=kolom_grid, padx=15, pady=10)

    def kembali(self):
        if hasattr(self.master, 'is_master') and self.master.is_master:
            self.fungsi_navigasi("rombel-select")
        else:
            self.fungsi_navigasi("welcome")

class StudentDetailScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        self.id_list = []
        self.current_index = 0
        
        self.top_section = ctk.CTkFrame(self, fg_color="transparent")
        self.top_section.pack(fill="both", expand=True, padx=40, pady=(30, 30))

        self.top_frame = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.left_frame = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=(5, 0))

        self.title_label = ctk.CTkLabel(self.top_frame, text="DATA MAHASISWA", text_color=C["primary"], font=("Arial", 45, "bold"), justify="left")
        self.title_label.pack(anchor="center", pady=(0, 20))
        
        self.card_info = ctk.CTkFrame(self.left_frame, fg_color=C["btn"], corner_radius=15, height=250)
        self.card_info.pack(fill="x")
        self.card_info.pack_propagate(False)
        
        # --- PERUBAHAN TATA LETAK GRID (TITIK DUA SEJAJAR) ---
        self.grid_info = ctk.CTkFrame(self.card_info, fg_color="transparent")
        self.grid_info.pack(anchor="w", padx=20, pady=(40, 10))

        font_label = ("Arial", 22, "bold")
        warna_teks = C["white"]

        # Baris 0: Nama
        ctk.CTkLabel(self.grid_info, text="Nama", text_color=warna_teks, font=font_label).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(self.grid_info, text=":", text_color=warna_teks, font=font_label).grid(row=0, column=1, sticky="w", padx=15, pady=(0, 6))
        self.val_nama = ctk.CTkLabel(self.grid_info, text="-", text_color=warna_teks, font=font_label, wraplength=280, justify="left")
        self.val_nama.grid(row=0, column=2, sticky="w", pady=(0, 6))

        # Baris 1: NIM
        ctk.CTkLabel(self.grid_info, text="NIM", text_color=warna_teks, font=font_label).grid(row=1, column=0, sticky="w", pady=4)
        ctk.CTkLabel(self.grid_info, text=":", text_color=warna_teks, font=font_label).grid(row=1, column=1, sticky="w", padx=15, pady=4)
        self.val_nim = ctk.CTkLabel(self.grid_info, text="-", text_color=warna_teks, font=font_label)
        self.val_nim.grid(row=1, column=2, sticky="w", pady=4)

        # Baris 2: Kelas
        ctk.CTkLabel(self.grid_info, text="Kelas", text_color=warna_teks, font=font_label).grid(row=2, column=0, sticky="w", pady=4)
        ctk.CTkLabel(self.grid_info, text=":", text_color=warna_teks, font=font_label).grid(row=2, column=1, sticky="w", padx=15, pady=4)
        self.val_kelas = ctk.CTkLabel(self.grid_info, text="-", text_color=warna_teks, font=font_label)
        self.val_kelas.grid(row=2, column=2, sticky="w", pady=4)

        # Baris 3: Status
        ctk.CTkLabel(self.grid_info, text="Status", text_color=warna_teks, font=font_label).grid(row=3, column=0, sticky="w", pady=4)
        ctk.CTkLabel(self.grid_info, text=":", text_color=warna_teks, font=font_label).grid(row=3, column=1, sticky="w", padx=15, pady=4)
        self.val_status = ctk.CTkLabel(self.grid_info, text="-", text_color=warna_teks, font=font_label)
        self.val_status.grid(row=3, column=2, sticky="w", pady=4)
        # -----------------------------------------------------

        self.right_frame = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.right_frame.pack(side="right", fill="y", padx=(0, 0), pady=(0, 0))
        
        self.opsi_bulatan = [
            {"label": "  I  ", "kolom": "status", "nilai": "izin", "warna_aktif": "#1d4e89"},
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
            ukuran = 70 
            
            btn_bulat = ctk.CTkButton(self.right_frame, text=item["label"], font=("Arial", 26, "bold"), text_color=C["white"], fg_color=C["btn"], hover_color=C["btn_hover"], width=ukuran, height=ukuran, corner_radius=ukuran // 2, command=lambda k=item["kolom"], n=item["nilai"]: self.proses_presensi_visual(k, n))
            btn_bulat.grid(row=baris, column=kolom, padx=8, pady=8)
            self.tombol_bulat_list.append(btn_bulat)

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
                
                # Update langsung nilai datanya (karena awalan label sudah di-hardcode)
                self.val_nama.configure(text=nama)
                self.val_nim.configure(text=nim)
                self.val_kelas.configure(text=kelas)
                
                if status == "hadir":
                    str_datang = datang.title() if datang else "-"
                    str_pulang = pulang.title() if pulang else "-"
                    teks_status = f"Hadir ({str_datang} | {str_pulang})"
                else:
                    teks_status = status.title()
                    
                self.val_status.configure(text=teks_status)
                
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