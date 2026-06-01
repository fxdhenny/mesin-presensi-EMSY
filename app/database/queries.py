# app/database/queries.py
import sqlite3
import csv
import os
from datetime import datetime

# =====================================================================
# FUNGSI INTERNAL: Mengambil Angkatan Aktif dari Tabel Pengaturan
# =====================================================================
def get_current_batch(cursor):
    cursor.execute("SELECT nilai FROM pengaturan WHERE kunci = 'current_batch'")
    res = cursor.fetchone()
    return res[0] if res else "ATMI59"

# =====================================================================
# 1. INISIALISASI PRESENSI (Dipanggil saat Layar Rombel dibuka)
# =====================================================================
def inisialisasi_presensi(db_path, kelas, rombel):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    hari_ini = datetime.now().strftime("%Y-%m-%d")
    batch = get_current_batch(cursor)
    
    # Hanya cari mahasiswa yang kelas, rombel, DAN angkatannya cocok
    cursor.execute('''
        SELECT id FROM mahasiswa 
        WHERE target_kelas = ? AND target_rombel = ? AND angkatan = ?
    ''', (kelas, rombel, batch))
    mahasiswa_list = cursor.fetchall()
    
    # Buat papan tulis harian (alfa) jika belum ada
    for (mhs_id,) in mahasiswa_list:
        cursor.execute('''
            SELECT id FROM presensi_harian 
            WHERE mahasiswa_id = ? AND tanggal = ?
        ''', (mhs_id, hari_ini))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO presensi_harian (mahasiswa_id, tanggal, status)
                VALUES (?, ?, 'alfa')
            ''', (mhs_id, hari_ini))
            
    conn.commit()
    conn.close()

# =====================================================================
# 2. AMBIL DATA PRESENSI (Untuk grid NIM di UI)
# =====================================================================
def ambil_data_presensi_hari_ini(db_path, kelas, rombel):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    hari_ini = datetime.now().strftime("%Y-%m-%d")
    batch = get_current_batch(cursor)
    
    cursor.execute('''
        SELECT p.id, m.nama, m.nim, p.status, p.kedatangan, p.kepulangan
        FROM presensi_harian p
        JOIN mahasiswa m ON p.mahasiswa_id = m.id
        WHERE m.target_kelas = ? AND m.target_rombel = ? 
          AND m.angkatan = ? AND p.tanggal = ?
        ORDER BY m.nim ASC
    ''', (kelas, rombel, batch, hari_ini))
    
    data = cursor.fetchall()
    conn.close()
    return data

# =====================================================================
# 3. UPDATE STATUS (Dipanggil saat menekan bulatan I/S/HT/TL)
# =====================================================================
def update_status_presensi(db_path, id_presensi, kolom, nilai):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    waktu_sekarang = datetime.now().strftime("%H:%M:%S")
    
    # Update data di presensi_harian
    cursor.execute(f"UPDATE presensi_harian SET {kolom} = ? WHERE id = ?", (nilai, id_presensi))
    
    # Catat sejarah perubahan di presensi_logs
    perubahan = f"{kolom} diubah menjadi {nilai}"
    cursor.execute('''
        INSERT INTO presensi_logs (attendance_id, perubahan, waktu)
        VALUES (?, ?, ?)
    ''', (id_presensi, perubahan, waktu_sekarang))
    
    conn.commit()
    conn.close()

# =====================================================================
# 4. EXPORT DATA (Berdasarkan Angkatan Aktif)
# =====================================================================
def export_to_flashdisk(db_path, seluruh_tanggal, tgl_awal, tgl_akhir, opsi_presensi, opsi_log, target_dir):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        batch = get_current_batch(cursor)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pesan = "Berhasil Mengekspor:\n"
        
        # Kondisi dasar: Ekspor HANYA milik angkatan aktif
        query_kondisi = "m.angkatan = ?"
        params = [batch]
        
        if not seluruh_tanggal:
            ta = datetime.strptime(tgl_awal, "%d/%m/%Y").strftime("%Y-%m-%d")
            tk = datetime.strptime(tgl_akhir, "%d/%m/%Y").strftime("%Y-%m-%d")
            query_kondisi += " AND p.tanggal BETWEEN ? AND ?"
            params.extend([ta, tk])
        
        if opsi_presensi:
            file_harian = os.path.join(target_dir, f"Presensi_{batch}_{timestamp}.csv")
            cursor.execute(f'''
                SELECT p.tanggal, m.nim, m.nama, m.target_kelas, m.target_rombel, p.status, p.kedatangan, p.kepulangan
                FROM presensi_harian p
                JOIN mahasiswa m ON p.mahasiswa_id = m.id
                WHERE {query_kondisi}
                ORDER BY p.tanggal DESC, m.target_kelas, m.target_rombel, m.nim
            ''', params)
            data = cursor.fetchall()
            with open(file_harian, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Tanggal", "NIM", "Nama", "Kelas", "Rombel", "Status", "Kedatangan", "Kepulangan"])
                writer.writerows(data)
            pesan += f"- {len(data)} baris Harian\n"
            
        if opsi_log:
            file_log = os.path.join(target_dir, f"Log_{batch}_{timestamp}.csv")
            cursor.execute(f'''
                SELECT p.tanggal, m.nim, m.nama, l.waktu, l.perubahan
                FROM presensi_logs l
                JOIN presensi_harian p ON l.attendance_id = p.id
                JOIN mahasiswa m ON p.mahasiswa_id = m.id
                WHERE {query_kondisi}
                ORDER BY p.tanggal DESC, l.waktu DESC
            ''', params)
            data_log = cursor.fetchall()
            with open(file_log, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Tanggal", "NIM", "Nama", "Waktu Eksekusi", "Perubahan (Log)"])
                writer.writerows(data_log)
            pesan += f"- {len(data_log)} baris Log\n"

        conn.close()
        return True, pesan
    except Exception as e:
        return False, f"Terjadi Kesalahan:\n{str(e)}"

# =====================================================================
# 5. RESET DATA PRESENSI
# =====================================================================
def hapus_semua_presensi(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM presensi_logs")
        cursor.execute("DELETE FROM presensi_harian")
        conn.commit()
        conn.close()
        return True
    except:
        return False