import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'attendance.db')

def create_database():
    print(f"[*] Menciptakan database EMSY di: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('PRAGMA journal_mode=WAL;')
    cursor.execute('PRAGMA foreign_keys=ON;')

    print("[*] Membuat tabel 'mahasiswa'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no INTEGER,
            nim TEXT UNIQUE,
            nama TEXT,
            target_kelas TEXT,
            target_rombel TEXT
        )
    ''')

    print("[*] Membuat tabel 'rfid_cards'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rfid_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid_uid TEXT UNIQUE,
            role INTEGER,
            kelas TEXT,
            rombel TEXT
        )
    ''')

    print("[*] Membuat tabel 'presensi_harian'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presensi_harian (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mahasiswa_id INTEGER,
            tanggal DATE,
            status TEXT DEFAULT 'alfa',
            kedatangan TEXT,
            kepulangan TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(mahasiswa_id) REFERENCES mahasiswa(id),
            UNIQUE(mahasiswa_id, tanggal)
        )
    ''')

    print("[*] Membuat tabel 'presensi_logs'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presensi_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_id INTEGER,
            perubahan TEXT,
            waktu DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(attendance_id) REFERENCES presensi_harian(id) ON DELETE CASCADE
        )
    ''')

    print("[*] Menambahkan Trigger untuk updated_at...")
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trigger_update_timestamp
        AFTER UPDATE ON presensi_harian
        FOR EACH ROW
        BEGIN
            UPDATE presensi_harian 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = OLD.id;
        END;
    ''')

    print("[*] Menambahkan Trigger untuk Audit Log (presensi_logs)...")
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trigger_log_perubahan
        AFTER UPDATE ON presensi_harian
        FOR EACH ROW
        WHEN (OLD.status != NEW.status OR OLD.kedatangan != NEW.kedatangan OR OLD.kepulangan != NEW.kepulangan)
        BEGIN
            INSERT INTO presensi_logs (attendance_id, perubahan)
            VALUES (
                OLD.id,
                'Status: ' || OLD.status || ' -> ' || NEW.status || 
                ' | Datang: ' || IFNULL(OLD.kedatangan, 'Kosong') || ' -> ' || IFNULL(NEW.kedatangan, 'Kosong') || 
                ' | Pulang: ' || IFNULL(OLD.kepulangan, 'Kosong') || ' -> ' || IFNULL(NEW.kepulangan, 'Kosong')
            );
        END;
    ''')

    conn.commit()
    conn.close()
    print("[+] Database EMSY beserta sistem Audit Log siap digunakan!")

if __name__ == '__main__':
    create_database()