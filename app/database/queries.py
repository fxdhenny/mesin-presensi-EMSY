import sqlite3
import csv
import os
from datetime import datetime

def export_to_flashdisk(db_path):
    """
    Fungsi untuk menarik data presensi dan menyimpannya ke Flashdisk USB
    """
    # 1. Mencari Flashdisk yang tertancap
    # Ganti 'admin' dengan username OS Raspberry Pi Anda jika berbeda
    try:
        username_os = os.getlogin() 
    except OSError:
        # Fallback yang lebih aman jika os.getlogin() gagal di beberapa OS Linux
        import getpass
        username_os = getpass.getuser()
        
    media_path = f"/media/{username_os}"
    
    if not os.path.exists(media_path) or not os.listdir(media_path):
        return False, "Flashdisk tidak terdeteksi. Pastikan sudah tertancap dengan benar."
    
    # Mengambil folder flashdisk pertama yang terdeteksi
    flashdisk_name = os.listdir(media_path)[0]
    flashdisk_path = os.path.join(media_path, flashdisk_name)
    
    # Membuat nama file otomatis berdasarkan tanggal hari ini
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nama_file = f"Rekap_Presensi_EMSY_{tanggal_hari_ini}.csv"
    jalur_simpan = os.path.join(flashdisk_path, nama_file)

    try:
        # 2. Menarik data gabungan dari Database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query JOIN untuk menggabungkan tabel presensi dengan data identitas mahasiswa
        cursor.execute('''
            SELECT 
                p.tanggal, m.target_kelas, m.target_rombel, m.no, m.nim, m.nama, 
                p.status, p.kedatangan, p.kepulangan, p.created_at, p.updated_at
            FROM presensi_harian p
            JOIN mahasiswa m ON p.mahasiswa_id = m.id
            ORDER BY p.tanggal DESC, m.target_kelas ASC, m.target_rombel ASC, m.no ASC
        ''')
        data_presensi = cursor.fetchall()
        
        # 3. Menulis ke file CSV di Flashdisk
        with open(jalur_simpan, mode='w', newline='', encoding='utf-8') as file_csv:
            writer = csv.writer(file_csv)
            # Menulis Header (Baris Judul)
            writer.writerow(['Tanggal', 'Kelas', 'Rombel', 'No. Absen', 'NIM', 'Nama Mahasiswa', 'Status', 'Kedatangan', 'Kepulangan', 'Waktu Input', 'Waktu Revisi'])
            # Menulis Isi Data
            writer.writerows(data_presensi)
            
        conn.close()
        return True, f"Berhasil diekspor ke: {nama_file}"

    except Exception as e:
        return False, f"Terjadi kesalahan saat ekspor: {str(e)}"
    
    # Pastikan ini ada di bagian paling atas file jika belum ada
from datetime import date

def inisialisasi_presensi(db_path, kelas, rombel):
    """
    Mencetak baris presensi default ('alfa') untuk seluruh anggota rombel hari ini.
    Fungsi ini kebal terhadap tap berkali-kali berkat INSERT OR IGNORE.
    """
    tanggal_hari_ini = date.today().strftime("%Y-%m-%d")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Ambil ID semua mahasiswa di rombel tersebut
        cursor.execute('''
            SELECT id FROM mahasiswa 
            WHERE target_kelas = ? AND target_rombel = ?
        ''', (kelas, rombel))
        daftar_mahasiswa = cursor.fetchall()
        
        # 2. Buatkan baris presensi untuk masing-masing anak
        for mhs in daftar_mahasiswa:
            mahasiswa_id = mhs[0]
            # INSERT OR IGNORE memastikan jika kartu di-tap 2x di hari yang sama,
            # sistem tidak akan menimpa data yang mungkin sudah direvisi menjadi 'hadir'
            cursor.execute('''
                INSERT OR IGNORE INTO presensi_harian (mahasiswa_id, tanggal, status)
                VALUES (?, ?, 'alfa')
            ''', (mahasiswa_id, tanggal_hari_ini))
            
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[-] Kesalahan saat inisialisasi presensi: {e}")
        return False

def ambil_data_presensi_hari_ini(db_path, kelas, rombel):
    """
    Menarik data presensi rombel hari ini untuk ditampilkan di GUI.
    """
    tanggal_hari_ini = date.today().strftime("%Y-%m-%d")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # JOIN untuk menggabungkan nama dari tabel mahasiswa dengan status dari presensi_harian
        cursor.execute('''
    SELECT 
        p.id,
        m.no,
        m.nim,
        m.nama,
        p.status,
        p.kedatangan,
        p.kepulangan
    FROM presensi_harian p
    JOIN mahasiswa m 
        ON p.mahasiswa_id = m.id
    WHERE m.target_kelas = ? 
      AND m.target_rombel = ?
      AND p.tanggal = ?
    ORDER BY m.no ASC
''', (kelas, rombel, tanggal_hari_ini))
        
        hasil = cursor.fetchall()
        conn.close()
        return hasil
        
    except Exception as e:
        print(f"[-] Kesalahan saat mengambil data presensi: {e}")
        return []

def update_status_presensi(db_path, attendance_id, kolom, nilai_baru):
    """
    Memperbarui kolom spesifik (status/kedatangan/kepulangan) saat tombol GUI ditekan.
    Contoh penggunaan: update_status_presensi(db_path, 15, 'status', 'hadir')
    """
    # Validasi keamanan untuk mencegah SQL Injection
    kolom_valid = ['status', 'kedatangan', 'kepulangan']
    if kolom not in kolom_valid:
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f"UPDATE presensi_harian SET {kolom} = ? WHERE id = ?"
        cursor.execute(query, (nilai_baru, attendance_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[-] Kesalahan saat update presensi: {e}")
        return False
    
    