import time

# =====================================================================
# SISTEM DETEKSI HARDWARE OTOMATIS
# =====================================================================
try:
    import RPi.GPIO as GPIO  # type: ignore
    from mfrc522 import SimpleMFRC522  # type: ignore
    HARDWARE_MODE = True
    print("[*] Sistem Hardware Terdeteksi: Mode Raspberry Pi Aktif")
except ImportError:
    # Jika gagal meng-import RPi.GPIO, berarti kita sedang di Laptop
    HARDWARE_MODE = False
    print("[!] Sistem Hardware TIDAK Terdeteksi: Mode Simulasi (Laptop) Aktif")

class RFIDReader:
    def __init__(self):
        self.last_scan_time = 0
        self.cooldown = 2.0  # 2 detik jeda
        
        if HARDWARE_MODE:
            self.reader = SimpleMFRC522()
        else:
            self.reader = None # Tidak pakai sensor fisik di mode simulasi

    def baca_kartu(self):
        waktu_sekarang = time.time()
        
        # Mencegah pembacaan beruntun (Debounce)
        if waktu_sekarang - self.last_scan_time < self.cooldown:
            return None

        if HARDWARE_MODE:
            # --- MODE RASPBERRY PI (SENSOR ASLI) ---
            try:
                uid, text = self.reader.read()
                self.last_scan_time = waktu_sekarang
                return str(uid)
            except Exception as e:
                print(f"[-] Error Sensor: {e}")
                return None
        else:
            # --- MODE SIMULASI LAPTOP (KEYBOARD) ---
            try:
                # Meminta input manual dari keyboard sebagai pengganti tap kartu
                uid_simulasi = input("\n[SIMULASI] Ketik UID Kartu (atau tekan Enter untuk lewat): ").strip()
                if uid_simulasi:
                    self.last_scan_time = waktu_sekarang
                    return uid_simulasi
                return None
            except KeyboardInterrupt:
                return None

# =====================================================================
# BLOK PENGUJIAN FASE 1
# =====================================================================
if __name__ == '__main__':
    print("\n[*] Menjalankan Pengujian RFID Service...")
    sensor = RFIDReader()
    
    try:
        while True:
            if HARDWARE_MODE:
                print(">> Silakan tap kartu fisik ke sensor RC522...")
            
            uid_terbaca = sensor.baca_kartu()
            
            if uid_terbaca:
                print(f"\n[+] BEEP! Data Terdeteksi.")
                print(f"[+] UID : {uid_terbaca}")
                print("-" * 30)
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n[*] Pengujian dihentikan.")
    finally:
        if HARDWARE_MODE:
            GPIO.cleanup()
            print("[*] Pin GPIO telah dibersihkan.")