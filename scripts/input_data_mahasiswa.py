import os
import sys
import csv
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'attendance.db')

def get_current_batch(cursor):
    cursor.execute("SELECT nilai FROM pengaturan WHERE kunci = 'current_batch'")
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def import_data_mahasiswa(file_path):
    if not os.path.exists(file_path):
        print(f"[-] Error: File {file_path} tidak ditemukan!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    angkatan_aktif = get_current_batch(cursor)
    if not angkatan_aktif:
        print("[-] Error: Pengaturan 'current_batch' tidak ditemukan di database.")
        conn.close()
        return

    print(f"[*] Angkatan Aktif saat ini: {angkatan_aktif}")
    print(f"[*] Membaca file: {file_path}\n")

    berhasil = 0
    gagal = 0
    detail_gagal = []

    ekstensi = os.path.splitext(file_path)[1].lower()
    data_baris = []

    try:
        # --- LOGIKA BACA UNTUK .CSV ---
        if ekstensi == '.csv':
            with open(file_path, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    data_baris.append(row)

        # --- LOGIKA BACA UNTUK .XLSX ---
        elif ekstensi == '.xlsx':
            try:
                import openpyxl
            except ImportError:
                print("[-] Error: Library 'openpyxl' belum terpasang. Jalankan: pip install openpyxl")
                conn.close()
                return

            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook.active
            
            # Membaca header di baris pertama
            headers = [cell.value.strip().lower() if cell.value else f"col_{i}" for i, cell in enumerate(sheet[1])]
            
            # Membaca isi data mulai dari baris kedua
            for row in sheet.iter_rows(min_row=2, values_only=True):
                # Ubah baris data menjadi dictionary agar strukturnya sama dengan CSV
                row_dict = {headers[i]: str(value).strip() if value is not None else "" for i, value in enumerate(row)}
                data_baris.append(row_dict)
        else:
            print(f"[-] Error: Format file '{ekstensi}' tidak didukung. Gunakan .csv atau .xlsx")
            conn.close()
            return

        # --- PROSES INJEKSI DATA ---
        for baris_index, row in enumerate(data_baris, start=1):
            nim = row.get('nim', '')
            nama = row.get('nama', '')
            kelas = row.get('kelas', '')
            rombel = row.get('rombel', '')

            if not nim or not nama or not kelas or not rombel:
                gagal += 1
                detail_gagal.append(f"Baris {baris_index}: Data tidak lengkap.")
                continue

            try:
                cursor.execute('''
                    INSERT INTO mahasiswa (nim, nama, angkatan, target_kelas, target_rombel)
                    VALUES (?, ?, ?, ?, ?)
                ''', (nim, nama, angkatan_aktif, kelas, rombel))
                berhasil += 1
                
            except sqlite3.IntegrityError:
                gagal += 1
                detail_gagal.append(f"Baris {baris_index}: NIM {nim} sudah terdaftar di {angkatan_aktif}.")
        
        conn.commit()

    except Exception as e:
        print(f"[-] Terjadi kesalahan saat membaca data: {e}")
    finally:
        conn.close()

    # --- TAMPILKAN RINGKASAN UI ---
    print("==========================================")
    print("           RINGKASAN IMPORT               ")
    print("==========================================")
    print(f"File         : {os.path.basename(file_path)}")
    print(f"Target Batch : {angkatan_aktif}")
    print(f"Total Baris  : {berhasil + gagal}")
    print(f"Berhasil     : {berhasil}")
    print(f"Gagal        : {gagal}")
    
    if detail_gagal:
        print("\nCatatan Gagal:")
        for catatan in detail_gagal[:5]:
            print(f" - {catatan}")
        if len(detail_gagal) > 5:
            print(f" - ... dan {len(detail_gagal) - 5} lainnya.")
    print("==========================================")

if __name__ == "__main__":
    # Anda bisa mengganti nama file di bawah ini menjadi 'data_maba.xlsx' 
    # jika Anda sudah menaruh file Excel-nya di dalam folder data/
    file_target = os.path.join(BASE_DIR, 'data', 'data_maba.xlsx')
    
    if not os.path.exists(file_target):
        print(f"[-] Tidak menemukan file {file_target} untuk diuji coba.")
        print("[*] Harap letakkan file Excel Anda di dalam folder data/")
    else:
        import_data_mahasiswa(file_target)