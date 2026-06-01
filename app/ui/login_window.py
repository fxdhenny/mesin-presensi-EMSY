# app/ui/login_window.py
import customtkinter as ctk
from datetime import datetime
from ui.colors import C

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
        self.label_welcome.pack(pady=(0, 15))

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

        self.btn_demo_rombel = ctk.CTkButton(self.demo_frame, text="TAP — KARTU ROMBEL", fg_color=C["btn"], hover_color=C["btn_hover"], text_color=C["white"], font=("Arial", 11, "bold"), corner_radius=14, height=38, command=lambda: master.proses_login("702964954886"))
        self.btn_demo_rombel.pack(side="left", padx=6)

        self.btn_demo_master = ctk.CTkButton(self.demo_frame, text="TAP — KARTU MASTER", fg_color=C["primary"], hover_color="#5a4c3e", text_color=C["white"], font=("Arial", 11, "bold"), corner_radius=14, height=38, command=lambda: master.proses_login("290744317040"))
        self.btn_demo_master.pack(side="left", padx=6)

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