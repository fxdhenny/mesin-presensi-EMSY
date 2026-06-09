# app/ui/screens.py
import os
import sys
import sqlite3
import platform
import string
import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime

# Konfigurasi jalur database (naik 3 tingkat dari folder ui)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import queries
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'attendance.db')

# =====================================================================
# FUNGSI DETEKSI FLASHDISK (Otomatis deteksi Windows / Linux)
# =====================================================================
def deteksi_path_flashdisk():
    sistem_operasi = platform.system()
    
    if sistem_operasi == "Windows":
        for huruf_drive in string.ascii_uppercase[3:]:  # Skip A, B, C
            path_drive = f"{huruf_drive}:\\"
            if os.path.exists(path_drive) and os.access(path_drive, os.W_OK):
                return path_drive
                
    elif sistem_operasi == "Linux":
        base_removable = "/media/"
        if os.path.exists(base_removable):
            for user_dir in os.listdir(base_removable):
                path_user = os.path.join(base_removable, user_dir)
                if os.path.isdir(path_user):
                    for usb_dir in os.listdir(path_user):
                        path_usb = os.path.join(path_user, usb_dir)
                        if os.access(path_usb, os.W_OK):
                            return path_usb
    return None

# =====================================================================
# KONFIGURASI WARNA
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

        self.label_welcome = ctk.CTkLabel(self.center_frame, text="WELCOME", text_color=C["text_dark"], font=("Poppins", 83, "bold"))
        self.label_welcome.pack(pady=(80, 10))

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

        self.demo_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.demo_frame.pack(pady=(35, 0))



        self.btn_master_login = ctk.CTkButton(
            self, text="M", fg_color=C["primary"], hover_color=C["btn_hover"],
            text_color=C["white"], font=("Arial", 20, "bold"), corner_radius=12,
            width=50, height=50,
            command=lambda: master.buka_popup_login_master()
        )
        self.btn_master_login.place(relx=1.0, rely=1.0, x=-25, y=-25, anchor="se")

    def update_waktu(self):
        sekarang = datetime.now()
        self.label_tanggal.configure(text=sekarang.strftime("%d %B %Y"))
        self.label_jam.configure(text=sekarang.strftime("%H:%M:%S"))
        self.after(1000, self.update_waktu)

    def ubah_status_scan(self, pesan, warna):
        self.box_scan.configure(border_color=warna)
        self.label_scan.configure(text=pesan, text_color=warna)

    def reset_status_scan(self):
        self.box_scan.configure(border_color=C["text_dark"])
        self.label_scan.configure(text="Please scan your Rfid!", text_color="black")


class MasterLoginPopup(ctk.CTkToplevel):
    def __init__(self, master_app):
        super().__init__(master_app)
        self.master_app = master_app
        self.title("Login Master")
        self.configure(fg_color=C["bg"])
        self.resizable(False, False)

        self.label_title = ctk.CTkLabel(self, text="LOGIN MASTER", font=("Arial", 24, "bold"), text_color=C["primary"])
        self.label_title.pack(pady=(20, 10), padx=20)

        self.entry_password = ctk.CTkEntry(self, width=280, show="*", font=("Arial", 16), placeholder_text="Masukkan password master")
        self.entry_password.pack(pady=(0, 10), padx=20)
        self.entry_password.bind("<Return>", lambda event: self.cek_password())

        self.label_status = ctk.CTkLabel(self, text="", font=("Arial", 12, "bold"), text_color="red")
        self.label_status.pack(pady=(0, 10), padx=20)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=(0, 20))

        self.btn_login = ctk.CTkButton(self.button_frame, text="LOGIN", fg_color=C["primary"], hover_color=C["btn_hover"], width=110, command=self.cek_password)
        self.btn_login.pack(side="left", padx=8)

        self.btn_cancel = ctk.CTkButton(self.button_frame, text="BATAL", fg_color="#888888", width=110, command=self.destroy)
        self.btn_cancel.pack(side="left", padx=8)

        self.update_idletasks()
        ew, eh = 360, 220
        ex = self.master_app.winfo_rootx() + (self.master_app.winfo_width() // 2) - (ew // 2)
        ey = self.master_app.winfo_rooty() + (self.master_app.winfo_height() // 2) - (eh // 2)
        self.geometry(f"{ew}x{eh}+{ex}+{ey}")
        self.transient(master_app)
        self.grab_set()

    def cek_password(self):
        password = self.entry_password.get().strip()
        if self.master_app.validate_master_password(password):
            self.label_status.configure(text="Akses master diberikan", text_color="#0b6623")
            self.master_app.is_master = True
            welcome_frame = self.master_app.frames.get("welcome")
            if welcome_frame:
                welcome_frame.ubah_status_scan("Akses master diberikan!", "#064e3b")
            self.destroy()
            self.master_app.fungsi_navigasi("rombel-select")
        else:
            self.label_status.configure(text="Password salah", text_color="#a11313")


class ChangePasswordPopup(ctk.CTkToplevel):
    def __init__(self, master_app):
        super().__init__(master_app)
        self.master_app = master_app
        self.title("Ganti Password Master")
        self.configure(fg_color=C["bg"])
        self.resizable(False, False)

        self.label_title = ctk.CTkLabel(self, text="GANTI PASSWORD", font=("Arial", 24, "bold"), text_color=C["primary"])
        self.label_title.pack(pady=(20, 10), padx=20)

        self.entry_new = ctk.CTkEntry(self, width=280, show="*", font=("Arial", 16), placeholder_text="Password baru")
        self.entry_new.pack(pady=(0, 10), padx=20)

        self.entry_confirm = ctk.CTkEntry(self, width=280, show="*", font=("Arial", 16), placeholder_text="Konfirmasi password")
        self.entry_confirm.pack(pady=(0, 10), padx=20)

        self.label_status = ctk.CTkLabel(self, text="", font=("Arial", 12, "bold"), text_color="red")
        self.label_status.pack(pady=(0, 10), padx=20)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=(0, 20))

        self.btn_save = ctk.CTkButton(self.button_frame, text="SIMPAN", fg_color=C["primary"], hover_color=C["btn_hover"], width=110, command=self.simpan_password)
        self.btn_save.pack(side="left", padx=8)

        self.btn_cancel = ctk.CTkButton(self.button_frame, text="BATAL", fg_color="#888888", width=110, command=self.destroy)
        self.btn_cancel.pack(side="left", padx=8)

        self.update_idletasks()
        ew, eh = 360, 260
        ex = self.master_app.winfo_rootx() + (self.master_app.winfo_width() // 2) - (ew // 2)
        ey = self.master_app.winfo_rooty() + (self.master_app.winfo_height() // 2) - (eh // 2)
        self.geometry(f"{ew}x{eh}+{ex}+{ey}")
        self.transient(master_app)
        self.grab_set()

    def simpan_password(self):
        new_password = self.entry_new.get().strip()
        confirm_password = self.entry_confirm.get().strip()

        if not new_password:
            self.label_status.configure(text="Password baru tidak boleh kosong", text_color="#a11313")
            return
        if new_password != confirm_password:
            self.label_status.configure(text="Konfirmasi tidak cocok", text_color="#a11313")
            return

        self.master_app.set_master_password(new_password)
        self.label_status.configure(text="Password master berhasil diubah", text_color="#0b6623")
        self.after(1500, self.destroy)


# =====================================================================
# LAYAR 2: LIST ROMBEL (800x480 Optimized)
# =====================================================================
class RombelSelectScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        self.sidebar = ctk.CTkFrame(self, width=120, fg_color=C["primary"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="R\nO\nM\nB\nE\nL", text_color=C["text"], font=("Arial", 40, "bold"))
        self.label_sidebar.pack(expand=True)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True)

        self.grid_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.grid_frame.pack(expand=True, pady=(10, 50))

        self.btn_export = ctk.CTkButton(
            self.grid_frame, text="EXPORT", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=120, height=40, 
            command=lambda: self.fungsi_navigasi("export-screen")
        )
        self.btn_export.grid(row=0, column=3, padx=(30, 15), pady=15)
        
        # --- TOMBOL UPDATE DATA (Menggantikan Tombol Reset Lama) ---
        self.btn_update = ctk.CTkButton(
            self.grid_frame, text="UPDATE", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=120, height=40, 
            command=lambda: UpdatePopup(self)
        )
        self.btn_update.grid(row=1, column=3, padx=(30, 15), pady=15)

        # --- TOMBOL UPDATE RFID ---
        self.btn_update_rfid = ctk.CTkButton(
            self.grid_frame, text="UPDATE RFID", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=120, height=40, 
            command=lambda: self.fungsi_navigasi("update-rfid")
        )
        self.btn_update_rfid.grid(row=2, column=3, padx=(30, 15), pady=15)

        self.btn_change_password = ctk.CTkButton(
            self.grid_frame, text="GANTI PASSWORD", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=120, height=40, 
            command=self.buka_popup_ganti_password
        )
        self.btn_change_password.grid(row=3, column=3, padx=(30, 15), pady=15)

        daftar_rombel = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
        
        for index, rombel in enumerate(daftar_rombel):
            baris = index // 3
            kolom = index % 3
            btn = ctk.CTkButton(self.grid_frame, text=rombel, fg_color=C["btn"], hover_color=C["btn_hover"], text_color=C["text"], font=("Arial", 32, "bold"), width=110, height=90, corner_radius=15, command=lambda r=rombel: self.fungsi_navigasi("nim-list", r))
            btn.grid(row=baris, column=kolom, padx=15, pady=15)

        self.btn_home = ctk.CTkButton(
            self.main_area, text="< BACK", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["white"], font=("Arial", 20, "bold"), 
            corner_radius=25, width=140, height=50, 
            command=lambda: self.fungsi_navigasi("welcome")
        )
        self.btn_home.place(x=40, y=400)

    def buka_popup_ganti_password(self):
        ChangePasswordPopup(self.master)


# =====================================================================
# LAYAR 2B: UPDATE RFID SELECTION
# =====================================================================
class UpdateRfidScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        self.sidebar = ctk.CTkFrame(self, width=120, fg_color=C["primary"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="R\nF\nI\nD", text_color=C["text"], font=("Arial", 40, "bold"))
        self.label_sidebar.pack(expand=True)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True)

        self.grid_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.grid_frame.pack(expand=True, pady=(10, 50))

        daftar_rombel = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
        for index, rombel in enumerate(daftar_rombel):
            baris = index // 3
            kolom = index % 3
            btn = ctk.CTkButton(
                self.grid_frame, text=rombel,
                fg_color=C["btn"], hover_color=C["btn_hover"],
                text_color=C["text"], font=("Arial", 32, "bold"),
                width=110, height=90, corner_radius=15,
                command=lambda r=rombel: UpdateRfidPopup(self, r)
            )
            btn.grid(row=baris, column=kolom, padx=15, pady=15)

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", side="bottom", padx=30, pady=(0, 25))

        self.btn_back = ctk.CTkButton(
            self.bottom_frame, text="< BACK",
            fg_color=C["primary"], hover_color="#5a4c3e",
            text_color=C["white"], font=("Arial", 20, "bold"),
            corner_radius=25, width=140, height=50,
            command=lambda: self.fungsi_navigasi("rombel-select")
        )
        self.btn_back.pack(side="left")


# =====================================================================
# LAYAR 3: NIM ANGGOTA ROMBEL
# =====================================================================
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


# =====================================================================
# LAYAR 4: DATA MAHASISWA (VERSI FINAL - SEJAJAR & FLEKSIBEL 1-2 BARIS)
# =====================================================================
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
        
        # Rumah Matriks Kotak Cokelat
        self.card_info = ctk.CTkFrame(self.left_frame, fg_color=C["btn"], corner_radius=15, width=480, height=250)
        self.card_info.pack(anchor="w", pady=(0, 0))
        self.card_info.pack_propagate(False)
        self.card_info.grid_propagate(False)
        for row_index in range(4):
            self.card_info.grid_rowconfigure(row_index, weight=1)
        self.card_info.grid_columnconfigure(0, minsize=110)
        self.card_info.grid_columnconfigure(1, minsize=30)
        self.card_info.grid_columnconfigure(2, minsize=320)
        
        # --- KOLOM 0: LABEL JUDUL (KIRI) ---
        self.lbl_t_nama = ctk.CTkLabel(self.card_info, text="Nama", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_t_nama.grid(row=0, column=0, padx=(25, 5), pady=(0, 6), sticky="w")
        
        self.lbl_t_nim = ctk.CTkLabel(self.card_info, text="NIM", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_t_nim.grid(row=1, column=0, padx=(25, 5), pady=6, sticky="w")
        
        self.lbl_t_kelas = ctk.CTkLabel(self.card_info, text="Kelas", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_t_kelas.grid(row=2, column=0, padx=(25, 5), pady=6, sticky="w")
        
        self.lbl_t_status = ctk.CTkLabel(self.card_info, text="Status", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_t_status.grid(row=3, column=0, padx=(25, 5), pady=6, sticky="w")
        
        # --- KOLOM 1: PENGUNCI TITIK DUA (TENGAH) ---
        self.lbl_c_nama = ctk.CTkLabel(self.card_info, text=":", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_c_nama.grid(row=0, column=1, padx=(0, 10), pady=(0, 6), sticky="w")
        
        self.lbl_c_nim = ctk.CTkLabel(self.card_info, text=":", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_c_nim.grid(row=1, column=1, padx=(0, 10), pady=6, sticky="w")
        
        self.lbl_c_kelas = ctk.CTkLabel(self.card_info, text=":", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_c_kelas.grid(row=2, column=1, padx=(0, 10), pady=6, sticky="w")
        
        self.lbl_c_status = ctk.CTkLabel(self.card_info, text=":", text_color=C["white"], font=("Arial", 22, "bold"))
        self.lbl_c_status.grid(row=3, column=1, padx=(0, 10), pady=6, sticky="w")
        
        # --- KOLOM 2: NILAI DATA DINAMIS (KANAN) ---
        # Diperlebar ke 350 piksel agar nama standar muat dalam 1 baris
        self.label_nama = ctk.CTkLabel(self.card_info, text="", text_color=C["white"], font=("Arial", 22, "bold"), wraplength=350, justify="left")
        self.label_nama.grid(row=0, column=2, padx=(0, 20), pady=(0, 6), sticky="w")
        
        self.label_nim = ctk.CTkLabel(self.card_info, text="", text_color=C["white"], font=("Arial", 22, "bold"))
        self.label_nim.grid(row=1, column=2, padx=(0, 20), pady=6, sticky="w")
        
        self.label_kelas = ctk.CTkLabel(self.card_info, text="", text_color=C["white"], font=("Arial", 22, "bold"))
        self.label_kelas.grid(row=2, column=2, padx=(0, 20), pady=6, sticky="w")
        
        self.label_status_info = ctk.CTkLabel(self.card_info, text="", text_color=C["white"], font=("Arial", 22, "bold"), wraplength=350, justify="left")
        self.label_status_info.grid(row=3, column=2, padx=(0, 20), pady=6, sticky="w")

        # Layout Tombol Bulat Presensi (Kanan)
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

        # Navigasi Bawah
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
                
                # Memasukkan data murni langsung ke Kolom 2
                self.label_nama.configure(text=nama)
                self.label_nim.configure(text=nim)
                self.label_kelas.configure(text=kelas)
                
                if status == "hadir":
                    str_datang = datang.title() if datang else "-"
                    str_pulang = pulang.title() if pulang else "-"
                    teks_status = f"Hadir ({str_datang} | {str_pulang})"
                else:
                    teks_status = status.title()
                    
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


# =====================================================================
# LAYAR 5: EXPORT SCREEN (Halaman Penuh)
# =====================================================================
class ExportScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True)
        
        self.label_judul = ctk.CTkLabel(self.main_container, text="EKSPOR DATA PRESENSI", text_color=C["primary"], font=("Arial", 35, "bold"))
        self.label_judul.pack(pady=(0, 20))

        self.frame_jenis = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_jenis.pack(pady=(0, 15))

        self.btn_harian_bg = ctk.CTkFrame(self.frame_jenis, fg_color=C["primary"], width=230, height=45, corner_radius=15)
        self.btn_harian_bg.pack(side="left", padx=15)
        self.btn_harian_bg.pack_propagate(False)

        self.label_harian = ctk.CTkLabel(self.btn_harian_bg, text="Presensi Harian", font=("Arial", 16, "bold"), text_color=C["white"])
        self.label_harian.pack(side="left", padx=(15, 0))

        self.check_harian_var = ctk.StringVar(value="off")
        self.check_harian = ctk.CTkCheckBox(
            self.btn_harian_bg, text="", width=24, height=24,
            variable=self.check_harian_var, onvalue="on", offvalue="off",
            fg_color=C["primary"], hover_color=C["btn_hover"], border_color=C["white"]
        )
        self.check_harian.pack(side="right", padx=(0, 15))

        self.btn_log_bg = ctk.CTkFrame(self.frame_jenis, fg_color=C["primary"], width=230, height=45, corner_radius=15)
        self.btn_log_bg.pack(side="left", padx=15)
        self.btn_log_bg.pack_propagate(False)

        self.label_log = ctk.CTkLabel(self.btn_log_bg, text="Log Presensi", font=("Arial", 16, "bold"), text_color=C["white"])
        self.label_log.pack(side="left", padx=(15, 0))

        self.check_log_var = ctk.StringVar(value="off")
        self.check_log = ctk.CTkCheckBox(
            self.btn_log_bg, text="", width=24, height=24,
            variable=self.check_log_var, onvalue="on", offvalue="off",
            fg_color=C["primary"], hover_color=C["btn_hover"], border_color=C["white"]
        )
        self.check_log.pack(side="right", padx=(0, 15))
        
        self.box_tanggal = ctk.CTkFrame(
            self.main_container, width=500, height=150,
            border_width=2, border_color=C["primary"], fg_color="transparent", corner_radius=15
        )
        self.box_tanggal.pack(pady=10)
        self.box_tanggal.pack_propagate(False)

        self.label_pilih = ctk.CTkLabel(self.box_tanggal, text="Pilih Tanggal :", text_color="black", font=("Arial", 20, "bold"))
        self.label_pilih.place(x=20, y=15)

        self.label_semua_tgl = ctk.CTkLabel(
            self.box_tanggal, text="Seluruh tanggal", font=("Arial", 18, "bold"), text_color="black"
        )
        self.label_semua_tgl.place(x=290, y=15)

        self.check_semua_tgl_var = ctk.StringVar(value="off")
        self.check_semua_tgl = ctk.CTkCheckBox(
            self.box_tanggal, text="", width=24, height=24,
            variable=self.check_semua_tgl_var, onvalue="on", offvalue="off",
            command=self.toggle_input_tanggal,
            fg_color=C["primary"], hover_color=C["btn_hover"], border_color=C["primary"]
        )
        self.check_semua_tgl.place(x=445, y=17) 

        self.label_awal = ctk.CTkLabel(self.box_tanggal, text="Awal", text_color="black", font=("Arial", 16, "bold"))
        self.label_awal.place(x=105, y=60)
        
        self.entry_awal = ctk.CTkEntry(
            self.box_tanggal, width=140, height=35, font=("Arial", 16),
            justify="center", fg_color="#3a3a3a", text_color="white", border_width=0,
            placeholder_text="DD/MM/YYYY", placeholder_text_color="#aaaaaa"
        )
        self.entry_awal.place(x=60, y=90)

        self.label_akhir = ctk.CTkLabel(self.box_tanggal, text="Akhir", text_color="black", font=("Arial", 16, "bold"))
        self.label_akhir.place(x=345, y=60)
        
        self.entry_akhir = ctk.CTkEntry(
            self.box_tanggal, width=140, height=35, font=("Arial", 16),
            justify="center", fg_color="#3a3a3a", text_color="white", border_width=0,
            placeholder_text="DD/MM/YYYY", placeholder_text_color="#aaaaaa"
        )
        self.entry_akhir.place(x=300, y=90)

        self.frame_tombol = ctk.CTkFrame(self.main_container, fg_color="transparent", width=500, height=50)
        self.frame_tombol.pack(pady=(20, 0))
        self.frame_tombol.pack_propagate(False)

        self.btn_back_export = ctk.CTkButton(
            self.frame_tombol, text="BACK", fg_color=C["btn"], hover_color=C["btn_hover"],
            text_color=C["white"], font=("Arial", 18, "bold"), corner_radius=15,
            width=120, height=45, command=lambda: self.fungsi_navigasi("rombel-select")
        )
        self.btn_back_export.pack(side="left")

        self.btn_proses_export = ctk.CTkButton(
            self.frame_tombol, text="EXPORT", fg_color=C["btn"], hover_color=C["btn_hover"],
            text_color=C["white"], font=("Arial", 18, "bold"), corner_radius=15,
            width=120, height=45, command=self.mulai_proses_ekspor
        )
        self.btn_proses_export.pack(side="right")

    def toggle_input_tanggal(self):
        if self.check_semua_tgl_var.get() == "on":
            self.entry_awal.configure(state="disabled", fg_color="#d3d3d3")
            self.entry_akhir.configure(state="disabled", fg_color="#d3d3d3")
        else:
            self.entry_awal.configure(state="normal", fg_color="#3a3a3a")
            self.entry_akhir.configure(state="normal", fg_color="#3a3a3a")

    def mulai_proses_ekspor(self):
        is_seluruh_tgl = (self.check_semua_tgl_var.get() == "on")
        tgl_awal = self.entry_awal.get() if not is_seluruh_tgl else None
        tgl_akhir = self.entry_akhir.get() if not is_seluruh_tgl else None

        opsi_presensi = (self.check_harian_var.get() == "on")
        opsi_log = (self.check_log_var.get() == "on")

        if not opsi_presensi and not opsi_log:
            self.tampilkan_pesan("Error", "Pilih minimal satu jenis data\nyang ingin diekspor!", "red")
            return

        if not is_seluruh_tgl:
            if not tgl_awal or not tgl_akhir:
                self.tampilkan_pesan("Error Input", "Tanggal awal dan akhir harus diisi!", "red")
                return
            try:
                datetime.strptime(tgl_awal, "%d/%m/%Y")
                datetime.strptime(tgl_akhir, "%d/%m/%Y")
            except ValueError:
                self.tampilkan_pesan("Error Input", "Format tanggal salah!\n\nHarap gunakan: DD/MM/YYYY", "red")
                return

        flashdisk_path = deteksi_path_flashdisk()
        if not flashdisk_path:
            self.tampilkan_pesan("Gagal", "Flashdisk tidak terdeteksi!\nSilakan colokkan flashdisk Anda.", "red")
            return

        print(f"[*] Mengekspor data ke flashdisk: {flashdisk_path}")
        sukses, pesan = queries.export_to_flashdisk(
            db_path=DB_PATH,
            seluruh_tanggal=is_seluruh_tgl,
            tanggal_awal=tgl_awal,
            tanggal_akhir=tgl_akhir,
            opsi_presensi=opsi_presensi,
            opsi_log=opsi_log,
            target_dir=flashdisk_path
        )

        if sukses:
            self.reset_input_tanggal()
            self.tampilkan_pesan("Sukses", pesan, "green", tutup_utama=True)
        else:
            self.tampilkan_pesan("Gagal", pesan, "red")

    def reset_input_tanggal(self):
        self.entry_awal.delete(0, "end")
        self.entry_akhir.delete(0, "end")
        self.check_semua_tgl_var.set("off")
        self.entry_awal.configure(state="normal", fg_color="#3a3a3a")
        self.entry_akhir.configure(state="normal", fg_color="#3a3a3a")

    def tampilkan_pesan(self, judul, pesan, warna_teks, tutup_utama=False):
        msg_popup = ctk.CTkToplevel(self)
        msg_popup.title(judul)
        msg_popup.configure(fg_color=C["bg"])
        
        ew, eh = 400, 180
        ex = self.winfo_rootx() + (self.winfo_width() // 2) - (ew // 2)
        ey = self.winfo_rooty() + (self.winfo_height() // 2) - (eh // 2)
        msg_popup.geometry(f"{ew}x{eh}+{ex}+{ey}")
        msg_popup.resizable(False, False)
        
        msg_popup.transient(self)
        msg_popup.wait_visibility() # Pengaman visual Linux Ubuntu
        msg_popup.grab_set()
        
        lbl_msg = ctk.CTkLabel(
            msg_popup, text=pesan, 
            font=("Arial", 16, "bold"), text_color=warna_teks,
            wraplength=350, justify="center"
        )
        lbl_msg.pack(expand=True, pady=(20, 10))
        
        def aksi_tutup():
            msg_popup.destroy()
            if tutup_utama:
                self.fungsi_navigasi("rombel-select")

        btn_ok = ctk.CTkButton(
            msg_popup, text="OK", fg_color=C["primary"], hover_color=C["btn_hover"], 
            width=100, corner_radius=10, command=aksi_tutup
        )
        btn_ok.pack(pady=(0, 20))


# =====================================================================
# POP-UP: KONFIRMASI UPDATE TOTAL (PENGGANTI RESET POPUP - FIX LINUX)
# =====================================================================
# =====================================================================
# POP-UP: KONFIRMASI UPDATE TOTAL (VERSI BERSIH TANPA DOUBLE X)
# =====================================================================
class UpdatePopup(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Konfirmasi Pembaruan")
        self.configure(fg_color="#fdfdfc")
        
        ew, eh = 500, 320
        ex = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - (ew // 2)
        ey = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - (eh // 2)
        self.geometry(f"{ew}x{eh}+{ex}+{ey}")
        self.resizable(False, False)
        
        self.transient(master)
        
        # ─── CRITICAL FIX UNTUK LINUX/UBUNTU ───
        self.wait_visibility() # Mencegah crash grab_set sebelum window siap di OS
        self.grab_set()
        
        # --- TOMBOL CLOSE CUSTOM (X) COKELAT SEBELUMNYA DI SINI TELAH DIHAPUS TOTAL ---
        
        self.frame_konfirmasi = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_konfirmasi.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.7)
        
        self.label_tanya = ctk.CTkLabel(
            self.frame_konfirmasi, 
            text="Apakah Anda ingin memperbarui data?\n\n*Sistem akan otomatis mem-backup data lama\nke flashdisk sebelum menimpanya.", 
            text_color="black", font=("Arial", 15, "bold"), justify="center"
        )
        self.label_tanya.pack(pady=(5, 20))
        
        self.frame_tombol_pilihan = ctk.CTkFrame(self.frame_konfirmasi, fg_color="transparent")
        self.frame_tombol_pilihan.pack()
        
        self.btn_ya = ctk.CTkButton(self.frame_tombol_pilihan, text="YA", font=("Arial", 16, "bold"), text_color="white", fg_color="#6c5b4b", hover_color="#5a4c3e", width=110, height=40, corner_radius=10, command=self.mulai_proses_update)
        self.btn_ya.pack(side="left", padx=15)
        
        self.btn_tidak = ctk.CTkButton(self.frame_tombol_pilihan, text="TIDAK", font=("Arial", 16, "bold"), text_color="white", fg_color="#b0957b", hover_color="#967e67", width=110, height=40, corner_radius=10, command=self.destroy)
        self.btn_tidak.pack(side="left", padx=15)

    def mulai_proses_update(self):
        flashdisk_path = deteksi_path_flashdisk()
        
        if not flashdisk_path:
            self.tampilkan_pesan("Proteksi Backup Gagal", "Flashdisk TIDAK terdeteksi!\n\nHarap colokkan USB Flashdisk ke Raspberry Pi untuk menampung arsip Auto-Backup sebelum memperbarui data mahasiswa.", "red")
            return

        file_terpilih = filedialog.askopenfilename(
            initialdir=flashdisk_path,
            title="Pilih Berkas Excel Mahasiswa Baru",
            filetypes=[("Excel Workbook", "*.xlsx")]
        )
        
        if not file_terpilih:
            return

        # 1. Jalankan Auto-Backup otomatis menyeluruh (Presensi + Logs)
        sukses_backup, pesan_backup = queries.ekspor_backup_otomatis_sebelum_ditimpa(DB_PATH, flashdisk_path)
        
        if not sukses_backup:
            self.tampilkan_pesan("Error Kritis", f"Proses dihentikan karena {pesan_backup}", "red")
            return

        # 2. Bersihkan database lama (Wipe bertahap sesuai hierarki Foreign Key)
        queries.bersihkan_seluruh_data_lama(DB_PATH)

        # 3. Baca dan suntik data mahasiswa dari berkas Excel baru
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        berhasil, gagal = 0, 0

        try:
            import openpyxl
            workbook = openpyxl.load_workbook(file_terpilih, data_only=True)
            sheet = workbook.active
            
            headers = [cell.value.strip().lower() if cell.value else f"col_{i}" for i, cell in enumerate(sheet[1])]
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = {headers[i]: str(value).strip() if value is not None else "" for i, value in enumerate(row)}
                
                nim = row_dict.get('nim', '')
                nama = row_dict.get('nama mahasiswa', '') # Presisi mencari kolom sesuai foto berkas Anda
                kelas = row_dict.get('kelas', '')
                rombel = row_dict.get('rombel', '')

                if nim.endswith('.0'): nim = nim[:-2]
                kelas = kelas.upper()
                if len(kelas) > 1: kelas = kelas[0]
                if rombel.endswith('.0'): rombel = rombel[:-2]

                if not nim or not nama or not kelas or not rombel:
                    gagal += 1
                    continue

                try:
                    cursor.execute('''
                        INSERT INTO mahasiswa (nim, nama, target_kelas, target_rombel)
                        VALUES (?, ?, ?, ?)
                    ''', (nim, nama, kelas, rombel))
                    berhasil += 1
                except sqlite3.IntegrityError:
                    gagal += 1

            conn.commit()
            
            pesan_final = f"{pesan_backup}\n\n=====================\n[+] UPDATE BERHASIL:\nTotal Sukses: {berhasil} Mahasiswa\nBaris Skip: {gagal}"
            self.tampilkan_pesan("Pembaruan Sukses", pesan_final, "green")
            self.destroy()

        except Exception as e:
            self.tampilkan_pesan("Error", f"Gagal membaca file: {str(e)}", "red")
        finally:
            conn.close()

    def tampilkan_pesan(self, judul, pesan, warna_teks):
        msg_popup = ctk.CTkToplevel(self.master)
        msg_popup.title(judul)
        msg_popup.configure(fg_color=C["bg"])
        ew, eh = 400, 220
        ex = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - (ew // 2)
        ey = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - (eh // 2)
        msg_popup.geometry(f"{ew}x{eh}+{ex}+{ey}")
        msg_popup.resizable(False, False)
        
        msg_popup.transient(self.master)
        msg_popup.wait_visibility() # Pengaman Linux Ubuntu pada sub-popup pesan
        msg_popup.grab_set()

        lbl_msg = ctk.CTkLabel(msg_popup, text=pesan, font=("Arial", 13, "bold"), text_color=warna_teks, wraplength=360, justify="center")
        lbl_msg.pack(expand=True, pady=(20, 10))
        btn_ok = ctk.CTkButton(msg_popup, text="OK", fg_color=C["primary"], hover_color=C["btn_hover"], width=100, corner_radius=10, command=msg_popup.destroy)
        btn_ok.pack(pady=(0, 20))


# =====================================================================
# LAYAR POP-UP: UPDATE RFID DETECTOR WINDOW (WITH COLLISION PROTECTION)
# =====================================================================
class UpdateRfidPopup(ctk.CTkToplevel):
    def __init__(self, master, rombel=None):
        super().__init__(master)
        self.title("Update RFID")
        self.configure(fg_color="#fdfdfc") 
        self.rombel = rombel
        
        # Ekstraksi huruf kelas dan angka rombel (Contoh: "B2" -> kelas="B", rombel="2")
        self.kelas_target = rombel[0] if rombel else ""
        self.rombel_target = rombel[1:] if rombel else ""
        
        ew, eh = 500, 300
        ex = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - (ew // 2)
        ey = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - (eh // 2)
        self.geometry(f"{ew}x{eh}+{ex}+{ey}")
        self.resizable(False, False)
        
        self.transient(master)
        self.wait_visibility() 
        self.grab_set()
        
        # Daftarkan pop-up ini ke jendela utama (main.py) agar main.py tahu 
        # bahwa hasil scan rfid harus dilempar ke sini, bukan ke menu login.
        # Hierarki: UpdateRfidPopup -> UpdateRfidScreen -> App (main.py)
        if hasattr(self.master.master, 'pendaftar_popup_aktif'):
            self.master.master.pendaftar_popup_aktif(self)
        
        # --- KOTAK COKELAT TAMPILAN UTAMA (Responsif Luas Bagian Tengah) ---
        self.box_rfid = ctk.CTkFrame(self, width=420, height=160, fg_color="#b0957b", corner_radius=20)
        self.box_rfid.place(relx=0.5, rely=0.5, anchor="center")
        self.box_rfid.pack_propagate(False)
        
        status_text = f"Tempelkan RFID baru\nuntuk Rombel {self.rombel}"
        self.label_status = ctk.CTkLabel(
            self.box_rfid, text=status_text, 
            text_color="white", font=("Arial", 18, "bold"), 
            justify="center", wraplength=380
        )
        self.label_status.place(relx=0.5, rely=0.5, anchor="center")
        
        # Pastikan jika jendela ditutup manual via Ubuntu X bar, ikatan listener dilepas
        self.protocol("WM_DELETE_WINDOW", self.aksi_tutup_popup)

    def terima_uid_scanned(self, uid_terbaca):
        """Fungsi yang menerima ketukan kartu saat pop-up sedang terbuka"""
        sukses, kode, pesan = queries.ubah_rfid_rombel_aman(
            DB_PATH, self.kelas_target, self.rombel_target, uid_terbaca
        )
        
        # 1. Atur warna kotak berdasarkan status keberhasilan
        if sukses:
            self.box_rfid.configure(fg_color="#1e4620")  # Hijau Daun
        else:
            if kode == "REDUNDAN":
                self.box_rfid.configure(fg_color="#cca010")  # Kuning Peringatan
            else:
                self.box_rfid.configure(fg_color="#7a2214")  # Merah Error
                
        # 2. Tampilkan pesan teks dari database
        self.label_status.configure(text=pesan, text_color="white")
        
        # 3. KUNCI UI/UX: Tutup otomatis pop-up dalam 2.5 detik untuk SEMUA kondisi!
        self.after(2500, self.aksi_tutup_popup)

    def aksi_tutup_popup(self):
        """Fungsi pembersihan memori dan navigasi redirect saat pop-up hancur"""
        # 1. Lepaskan ikatan penerima data sensor di app/main.py
        if hasattr(self.master.master, 'pendaftar_popup_aktif'):
            self.master.master.pendaftar_popup_aktif(None)
            
        # 2. Redirect: Kembalikan layar utama ke menu Daftar Rombel
        if hasattr(self.master, 'fungsi_navigasi'):
            self.master.fungsi_navigasi("rombel-select")
            
        # 3. Hancurkan jendela pop-up
        self.destroy()