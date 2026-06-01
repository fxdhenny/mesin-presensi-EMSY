# app/ui/master_window.py
import os
import sys
import csv
import sqlite3
import platform
import string
import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime

# Import konfigurasi dan palet warna
from ui.colors import C
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import queries
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'attendance.db')

def deteksi_path_flashdisk():
    sistem_operasi = platform.system()
    if sistem_operasi == "Windows":
        for huruf_drive in string.ascii_uppercase[3:]:
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

class RombelSelectScreen(ctk.CTkFrame):
    def __init__(self, master, fungsi_navigasi):
        super().__init__(master, fg_color=C["bg"])
        self.fungsi_navigasi = fungsi_navigasi

        # Sidebar Kiri
        self.sidebar = ctk.CTkFrame(self, width=120, fg_color=C["primary"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.label_sidebar = ctk.CTkLabel(self.sidebar, text="R\nO\nM\nB\nE\nL", text_color=C["text"], font=("Arial", 40, "bold"))
        self.label_sidebar.pack(expand=True)

        # Main Area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True)

        # Label Judul Menu Utama
        self.lbl_judul_main = ctk.CTkLabel(self.main_area, text="DASHBOARD KENDALI MASTER", text_color=C["primary"], font=("Arial", 26, "bold"))
        self.lbl_judul_main.pack(anchor="w", padx=40, pady=(40, 10))

        # Grid Area Konten Tombol
        self.grid_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.grid_frame.pack(expand=True, pady=(10, 60))
        
        # --- PANEL TOMBOL KENDALI MASTER (KOLOM KANAN) ---
        
        # 1. Tombol EXPORT MANUAL
        self.btn_export = ctk.CTkButton(
            self.grid_frame, text="EXPORT", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=130, height=40, 
            command=lambda: self.fungsi_navigasi("export-screen")
        )
        self.btn_export.grid(row=0, column=3, padx=(40, 15), pady=10)
        
        # 2. Tombol IMPORT MHS
        self.btn_import = ctk.CTkButton(
            self.grid_frame, text="IMPORT MHS", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=130, height=40, 
            command=self.pic_berkas_mahasiswa
        )
        self.btn_import.grid(row=1, column=3, padx=(40, 15), pady=10)
        
        # 3. TOMBOL UPDATE DATA (Ganti dari RESET menjadi UPDATE)
        self.btn_update = ctk.CTkButton(
            self.grid_frame, text="UPDATE", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=130, height=40, 
            command=lambda: UpdatePopup(self)  # Memanggil pop-up konfirmasi update baru
        )
        self.btn_update.grid(row=2, column=3, padx=(40, 15), pady=10)

        # 4. Tombol UPDATE RFID
        self.btn_update_rfid = ctk.CTkButton(
            self.grid_frame, text="UPDATE RFID", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["text"], font=("Arial", 14, "bold"), 
            corner_radius=10, width=130, height=40, 
            command=lambda: self.fungsi_navigasi("update-rfid")
        )
        self.btn_update_rfid.grid(row=3, column=3, padx=(40, 15), pady=10)

        # GRID TOMBOL PILIHAN ROMBEL FISIK LAB (A1 - C3)
        daftar_rombel = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
        for index, rombel in enumerate(daftar_rombel):
            baris = index // 3
            kolom = index % 3
            btn = ctk.CTkButton(self.grid_frame, text=rombel, fg_color=C["btn"], hover_color=C["btn_hover"], text_color=C["text"], font=("Arial", 32, "bold"), width=110, height=80, corner_radius=15, command=lambda r=rombel: self.fungsi_navigasi("nim-list", r))
            btn.grid(row=baris, column=kolom, padx=15, pady=10)

        self.btn_home = ctk.CTkButton(
            self.main_area, text="< BACK", 
            fg_color=C["primary"], hover_color="#5a4c3e", 
            text_color=C["white"], font=("Arial", 20, "bold"), 
            corner_radius=25, width=140, height=50, 
            command=lambda: self.fungsi_navigasi("welcome")
        )
        self.btn_home.place(x=40, y=410)

    def pic_berkas_mahasiswa(self):
        """Fungsi pembantu pencari berkas standar"""
        flashdisk_path = deteksi_path_flashdisk()
        if not flashdisk_path:
            flashdisk_path = os.path.expanduser("~")
        file_terpilih = filedialog.askopenfilename(
            initialdir=flashdisk_path,
            title="Pilih Berkas Excel Mahasiswa",
            filetypes=[("Excel atau CSV", "*.xlsx *.csv")]
        )
        return file_terpilih

    def tampilkan_popup_pesan(self, judul, pesan, warna):
        msg_popup = ctk.CTkToplevel(self)
        msg_popup.title(judul)
        msg_popup.configure(fg_color=C["bg"])
        ew, eh = 420, 240
        ex = self.winfo_rootx() + (self.winfo_width() // 2) - (ew // 2)
        ey = self.winfo_rooty() + (self.winfo_height() // 2) - (eh // 2)
        msg_popup.geometry(f"{ew}x{eh}+{ex}+{ey}")
        msg_popup.resizable(False, False)
        msg_popup.transient(self)
        msg_popup.grab_set()

        lbl = ctk.CTkLabel(msg_popup, text=pesan, font=("Arial", 14, "bold"), text_color=warna, justify="center", wraplength=380)
        lbl.pack(expand=True, pady=10)
        btn = ctk.CTkButton(msg_popup, text="OK", fg_color=C["primary"], width=100, command=msg_popup.destroy)
        btn.pack(pady=(0, 20))

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
            self.tampilkan_pesan("Sukses", pesan, "green", tutup_utama=True)
        else:
            self.tampilkan_pesan("Gagal", pesan, "red")

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
        msg_popup.grab_set()
        
        lbl_msg = ctk.CTkLabel(msg_popup, text=pesan, font=("Arial", 16, "bold"), text_color=warna_teks, wraplength=350, justify="center")
        lbl_msg.pack(expand=True, pady=(20, 10))
        
        def aksi_tutup():
            msg_popup.destroy()
            if tutup_utama:
                self.fungsi_navigasi("rombel-select")

        btn_ok = ctk.CTkButton(msg_popup, text="OK", fg_color=C["primary"], hover_color=C["btn_hover"], width=100, corner_radius=10, command=aksi_tutup)
        btn_ok.pack(pady=(0, 20))

# =====================================================================
# POP-UP BARU: KONFIRMASI UPDATE TOTAL (PENGGANTI RESET POPUP)
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
        self.grab_set()
        
        self.btn_close = ctk.CTkButton(self, text="×", font=("Arial", 28, "bold"), text_color="white", fg_color="#6c5b4b", hover_color="#5a4c3e", width=46, height=46, corner_radius=23, command=self.destroy)
        self.btn_close.place(x=430, y=20)
        
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
        """Menjalankan alur: Cek USB -> Pilih Excel -> Backup -> Overwrite"""
        flashdisk_path = deteksi_path_flashdisk()
        
        if not flashdisk_path:
            self.tampilkan_pesan("Proteksi Backup Gagal", "Flashdisk TIDAK terdeteksi!\n\nHarap colokkan USB Flashdisk ke Raspberry Pi untuk menampung arsip Auto-Backup sebelum memperbarui data mahasiswa.", "red")
            return

        # Buka penjelajah berkas
        file_terpilih = filedialog.askopenfilename(
            initialdir=flashdisk_path,
            title="Pilih Berkas Excel Mahasiswa Baru",
            filetypes=[("Excel Workbook", "*.xlsx")]
        )
        
        if not file_terpilih:
            return

        # 1. Jalankan Auto-Backup
        sukses_backup, pesan_backup = queries.ekspor_backup_otomatis_sebelum_ditimpa(DB_PATH, flashdisk_path)
        
        if not sukses_backup:
            self.tampilkan_pesan("Error Kritis", f"Proses dihentikan karena {pesan_backup}", "red")
            return

        # 2. Bersihkan database lama (Wipe)
        queries.bersihkan_seluruh_data_lama(DB_PATH)

        # 3. Baca dan suntik data mahasiswa dari file baru
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        berhasil, gagal = 0, 0

        try:
            import openpyxl
            workbook = openpyxl.load_workbook(file_terpilih, data_only=True)
            sheet = workbook.active
            
            # Ekstraksi header secara lowercase
            headers = [cell.value.strip().lower() if cell.value else f"col_{i}" for i, cell in enumerate(sheet[1])]
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = {headers[i]: str(value).strip() if value is not None else "" for i, value in enumerate(row)}
                
                # Pemetaan kolom presisi sesuai FOTO HEDER EXCEL USER
                nim = row_dict.get('nim', '')
                nama = row_dict.get('nama mahasiswa', '')  # Sesuai teks "Nama Mahasiswa" di foto
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
            self.frame_konfirmasi.destroy()
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
        msg_popup.grab_set()

        lbl_msg = ctk.CTkLabel(msg_popup, text=pesan, font=("Arial", 13, "bold"), text_color=warna_teks, wraplength=360, justify="center")
        lbl_msg.pack(expand=True, pady=(20, 10))
        btn_ok = ctk.CTkButton(msg_popup, text="OK", fg_color=C["primary"], hover_color=C["btn_hover"], width=100, corner_radius=10, command=msg_popup.destroy)
        btn_ok.pack(pady=(0, 20))
                
class UpdateRfidPopup(ctk.CTkToplevel):
    def __init__(self, master, rombel=None):
        super().__init__(master)
        self.title("Update RFID")
        self.configure(fg_color="#fdfdfc") 
        self.rombel = rombel
        ew, eh = 500, 300
        ex = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - (ew // 2)
        ey = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - (eh // 2)
        self.geometry(f"{ew}x{eh}+{ex}+{ey}")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self.btn_close = ctk.CTkButton(self, text="×", font=("Arial", 28, "bold"), text_color="white", fg_color="#6c5b4b", hover_color="#5a4c3e", width=46, height=46, corner_radius=23, command=self.destroy)
        self.btn_close.place(x=430, y=20)
        
        self.box_rfid = ctk.CTkFrame(self, width=340, height=100, fg_color="#b0957b", corner_radius=20)
        self.box_rfid.place(relx=0.5, rely=0.55, anchor="center")
        self.box_rfid.pack_propagate(False)
        
        status_text = "Tempelkan RFID"
        if self.rombel:
            status_text = f"Tempelkan RFID untuk {self.rombel}"
        self.label_status = ctk.CTkLabel(self.box_rfid, text=status_text, text_color="white", font=("Arial", 24, "normal"))
        self.label_status.place(relx=0.5, rely=0.5, anchor="center")