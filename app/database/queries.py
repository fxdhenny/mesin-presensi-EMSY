import os
import csv
import sqlite3
from datetime import datetime

# =====================================================================
# 1. INISIALISASI PRESENSI (Dipanggil saat masuk ke NimListScreen)
# =====================================================================
def inisialisasi_presensi(db_path, kelas, rombel):
    """
    Memeriksa dan menyalin data mahasiswa aktif ke tabel presensi_harian 
    jika hari ini mahasiswa di rombel tersebut belum terabsen.
    Secara default akan dimasukkan sebagai 'alfa'.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Ambil semua mahasiswa yang sesuai dengan kelas dan rombel target
        cursor.execute("""
            SELECT id FROM mahasiswa 
            WHERE target_kelas = ? AND target_rombel = ?
        """, (kelas, rombel))
        daftar_mahasiswa = cursor.fetchall()
        
        for (mahasiswa_id,) in daftar_mahasiswa:
            # Cek apakah hari ini mahasiswa tersebut sudah ada baris presensinya
            cursor.execute("""
                SELECT id FROM presensi_harian 
                WHERE mahasiswa_id = ? AND tanggal = ?
            """, (mahasiswa_id, tanggal_hari_ini))
            
            if not cursor.fetchone():
                # Jika belum ada, masukkan sebagai 'alfa' untuk mengawali hari
                cursor.execute("""
                    INSERT INTO presensi_harian (mahasiswa_id, tanggal, status, kedatangan, kepulangan)
                    VALUES (?, ?, 'alfa', NULL, NULL)
                """, (mahasiswa_id, tanggal_hari_ini))
                
        conn.commit()
    except sqlite3.Error as e:
        print(f"[-] Gagal inisialisasi presensi harian: {e}")
    finally:
        conn.close()


# =====================================================================
# 2. AMBIL DATA PRESENSI (Dipanggil untuk membuat tombol NIM)
# =====================================================================
def ambil_data_presensi_hari_ini(db_path, kelas, rombel):
    """
    Mengambil data presensi hari ini untuk ditampilkan di NimListScreen.
    Diurutkan berdasarkan ID database (sesuai urutan input).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
    data = []
    
    try:
        # ORDER BY m.id ASC agar urutannya sama persis seperti di database
        cursor.execute("""
            SELECT p.id, m.id, m.nim, m.nama, p.status, p.kedatangan, p.kepulangan
            FROM presensi_harian p
            JOIN mahasiswa m ON p.mahasiswa_id = m.id
            WHERE m.target_kelas = ? AND m.target_rombel = ? AND p.tanggal = ?
            ORDER BY m.id ASC
        """, (kelas, rombel, tanggal_hari_ini))
        data = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[-] Gagal mengambil data presensi hari ini: {e}")
    finally:
        conn.close()
    return data


# =====================================================================
# 3. UPDATE STATUS & LOG (Dipanggil di StudentDetailScreen)
# =====================================================================
def update_status_presensi(db_path, id_presensi, kolom, nilai):
    """
    Mengubah data presensi secara langsung dari UI 
    dan mencatat log perubahan ke tabel presensi_logs.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    waktu_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute(f"SELECT status, kedatangan, kepulangan FROM presensi_harian WHERE id = ?", (id_presensi,))
        lama = cursor.fetchone()
        
        if lama:
            status_lama, datang_lama, pulang_lama = lama
            
            # Update data presensi harian
            cursor.execute(f"UPDATE presensi_harian SET {kolom} = ? WHERE id = ?", (nilai, id_presensi))
            
            # Ambil data baru setelah diupdate
            cursor.execute(f"SELECT status, kedatangan, kepulangan FROM presensi_harian WHERE id = ?", (id_presensi,))
            baru = cursor.fetchone()
            status_baru, datang_baru, pulang_baru = baru
            
            # Format teks perubahan
            str_datang_lama = datang_lama if datang_lama else "Kosong"
            str_datang_baru = datang_baru if datang_baru else "Kosong"
            str_pulang_lama = pulang_lama if pulang_lama else "Kosong"
            str_pulang_baru = pulang_baru if pulang_baru else "Kosong"
            
            teks_perubahan = f"Status: {status_lama} -> {status_baru} | Datang: {str_datang_lama} -> {str_datang_baru} | Pulang: {str_pulang_lama} -> {str_pulang_baru}"
            
            # Tulis riwayat ke log
            cursor.execute("""
                INSERT INTO presensi_logs (attendance_id, perubahan, waktu)
                VALUES (?, ?, ?)
            """, (id_presensi, teks_perubahan, waktu_log))
            
            conn.commit()
    except sqlite3.Error as e:
        print(f"[-] Gagal mengupdate status presensi & log: {e}")
    finally:
        conn.close()


def hapus_semua_presensi(db_path):
    """
    Hapus semua data dari tabel presensi_logs dan presensi_harian.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM presensi_logs")
        cursor.execute("DELETE FROM presensi_harian")
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[-] Gagal menghapus data presensi: {e}")
        return False
    finally:
        conn.close()


# =====================================================================
# 4. EKSPOR KE FLASHDISK (Dipanggil dari Popup Export UI)
# =====================================================================
def export_to_flashdisk(db_path, seluruh_tanggal=True, tanggal_awal=None, tanggal_akhir=None, opsi_presensi=True, opsi_log=False, target_dir=None):
    """
    Mengekspor data presensi ke flashdisk dalam format CSV.
    """
    try:
        if not target_dir or not os.path.exists(target_dir):
            return False, "Flashdisk tidak terdeteksi! Silakan colokkan flashdisk terlebih dahulu."
        
        # Buat timestamp untuk nama file
        waktu_ekspor = datetime.now().strftime("%d-%m-%Y_%H%M%S")
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tgl_awal_db = tanggal_awal
        tgl_akhir_db = tanggal_akhir
        
        if not seluruh_tanggal:
            if tanggal_awal and "/" in tanggal_awal:
                tgl_awal_db = datetime.strptime(tanggal_awal, "%d/%m/%Y").strftime("%Y-%m-%d")
            if tanggal_akhir and "/" in tanggal_akhir:
                tgl_akhir_db = datetime.strptime(tanggal_akhir, "%d/%m/%Y").strftime("%Y-%m-%d")
        
        file_terekspor = []

        if opsi_presensi:
            query_presensi = """
                SELECT p.tanggal, m.nim, m.nama, m.target_kelas, m.target_rombel, p.status, p.kedatangan, p.kepulangan
                FROM presensi_harian p
                JOIN mahasiswa m ON p.mahasiswa_id = m.id
            """
            params_presensi = []
            if not seluruh_tanggal:
                query_presensi += " WHERE p.tanggal BETWEEN ? AND ?"
                params_presensi = [tgl_awal_db, tgl_akhir_db]
                
            query_presensi += " ORDER BY p.tanggal DESC, m.nim ASC"
            
            cursor.execute(query_presensi, params_presensi)
            rows_presensi = cursor.fetchall()
            
            if not rows_presensi:
                conn.close()
                return False, "Gagal Eksport: Data presensi tidak ditemukan pada tanggal tersebut!"
                
            csv_path_presensi = os.path.join(target_dir, f"export_data_presensi_{waktu_ekspor}.csv")
            with open(csv_path_presensi, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Tanggal", "NIM", "Nama", "Kelas", "Rombel", "Status", "Kedatangan", "Kepulangan"])
                writer.writerows(rows_presensi)
            
            file_terekspor.append("export_data_presensi.csv")

        if opsi_log:
            query_log = """
                SELECT p.tanggal, m.nim, m.nama, m.target_kelas, m.target_rombel, l.perubahan, l.waktu
                FROM presensi_logs l
                JOIN presensi_harian p ON l.attendance_id = p.id
                JOIN mahasiswa m ON p.mahasiswa_id = m.id
            """
            params_log = []
            if not seluruh_tanggal:
                query_log += " WHERE p.tanggal BETWEEN ? AND ?"
                params_log = [tgl_awal_db, tgl_akhir_db]
                
            query_log += " ORDER BY l.waktu DESC, m.nim ASC"
            
            cursor.execute(query_log, params_log)
            rows_log = cursor.fetchall()
            
            if not rows_log:
                conn.close()
                return False, "Gagal Eksport: Data log presensi tidak ditemukan pada tanggal tersebut!"
                
            csv_path_log = os.path.join(target_dir, f"export_log_presensi_{waktu_ekspor}.csv")
            with open(csv_path_log, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Tanggal", "NIM", "Nama", "Kelas", "Rombel", "Perubahan", "Waktu"])
                writer.writerows(rows_log)
                
            file_terekspor.append("export_log_presensi.csv")

        conn.close()
        
        if not file_terekspor:
            return False, "Tidak ada opsi ekspor yang dipilih."
            
        return True, f"Sukses! Berhasil memasukkan data ke flashdisk: {', '.join(file_terekspor)}"
        
    except Exception as e:
        return False, f"Gagal Eksport: {str(e)}"