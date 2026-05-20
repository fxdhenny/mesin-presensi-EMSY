import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'attendance.db')

# (Data Mentah 93 Mahasiswa tetap sama, saya singkat di sini agar rapi)
DATA_MENTAH = """
1	20246011	Bonaventura Brivaristo Embaratama	A	1
2	20246044	Marcellino Billy Fernando	A	1
3	20246047	Michael Gading Valentino	A	1
4	20246046	Matius Kamajaya Terang Damai	A	1
5	20242015	Daniel Kristian Saputra	A	1
6	20242021	Gangga Duta Rajesh Radenta	A	1
7	20242040	Sesilia Ina Pratiwi	A	1
8	20246052	Muhammad Nabil	A	1
9	20242018	Fransisca Xaveria Valencia Putri Nata	A	1
10	20242034	Louis Ladevik Chriesto Setiawan	A	1
11	20242028	Isidorus Aprilla Pulung Anggoro	A	2
12	20246001	Adhimas Juan Herjuna	A	2
13	20246023	Donisus Evander Fidelta	A	2
14	20246041	Leonardo Muliasakti Cahyo Potrodimedjo	A	2
15	20242036	Robby Suryo Suwirat	A	2
16	20246043	Manuel Juan Tama	A	2
17	20246024	Dominicus Mateo Nugroho	A	2
18	20242025	Huda Nidhar Supriyanto	A	2
19	20242032	Kimiko Olivia Ramadhani	A	2
20	20246035	Hubertus Hugh Setiawan	A	2
21	20246006	Andreas Daru Suryanata	A	3
22	20242004	Albertus Setyawan Kristiyadi	A	3
23	20242006	Alfonsus Geraldo	A	3
24	20246025	Dorothea Shinta Puspitasari	A	3
25	20242026	Ignatius Ammittoba Bimo Ariputra	A	3
26	20246032	Hammi Uma Iowa	A	3
27	20242013	Cleo Orlin Eldri Prabowo	A	3
28	20246022	Dionisus Bramantyo Kuncoro	A	3
29	20246017	Dagda Evan Kumara	A	3
30	20246059	Vladimir Narodya Volya Wijaya	A	3
31	20242020	Gabriel Jose Fabian	A	3
1	20246026	Efod Steven Santoso	B	1
2	20246020	Deno Caesanova Taryano	B	1
3	20246029	Frido Eka Setyanugroho	B	1
4	20242011	Antonius Rama Moriska	B	1
5	20246030	Gabriella Enya Setya Gratias	B	1
6	20246042	Mahza Fausta Nugraha	B	1
7	20242005	Aldino Satria Wibowo	B	1
8	20242010	Andreas Landung Wicaksono	B	1
9	20246053	Nathanael Hanindyo	B	1
10	20246049	Michael Setya Budi Santoso	B	1
11	20246021	Denyar Duta Harjanto	B	2
12	20246038	Josef Kevin Natanael	B	2
13	20242030	Josefa Arsanti Kalbu Dasih	B	2
14	20246002	Agustinus Radityo Putro Sri Raharjo	B	2
15	20246034	Heronimus Aditya Wijaya Suhartono	B	2
16	20242016	Dewantoro Nur Lukito	B	2
17	20242031	Jovan Kristanto	B	2
18	20242038	Samuel Satrio Wicaksono	B	2
19	20246018	Darrel Calvino Geraldo	B	2
20	20242023	Glorious Jan Neda	B	2
21	20246040	Laurentius Arya Putra Inigo Vipassana	B	3
22	20246005	Ananda Marchel Emanuel	B	3
23	20242012	Arnel Kharisma Octora	B	3
24	20246007	Anton Wisnu Maryanto	B	3
25	20242027	Ilham Hari Subroto	B	3
26	20242014	Danar Ernawan	B	3
27	20242037	Samuel Budiyanto Suwignyo	B	3
28	20242008	Alpheratz Indra Kusuma	B	3
29	20246058	Stefanus Raymond Subroto	B	3
30	20242033	Laurensia Sekar Winanti	B	3
31	20246003	Ambrosius Krisna Murti	B	3
1	20242039	Sean Audhie Marcelius	C	1
2	20246031	Guruh Viantara Putra	C	1
3	20246057	Stefanus Dastin Arifin	C	1
4	20246045	Margaretha Selly Dyapetriana Sulaksana	C	1
5	20246012	Caroluslwanga Putra Bima Perkasa Chrysdarmawan	C	1
6	20246009	Bagas Christizen Emanuel Hendrawan	C	1
7	20242035	Pieter Pulung Adi Setyawan	C	1
8	20246019	David Rido Patria	C	1
9	20246015	Christian Surya Saputro	C	1
10	20242002	Albert Wahyu Wibisono	C	1
11	20246051	Moses Ashrael Endrato	C	2
12	20246037	Jean Leonard Pranoto Japira	C	2
13	20246039	Kanisius Nikolas Candra	C	2
14	20246033	Hendrikus Novanciz Namu	C	2
15	20246008	Asa Ademulia	C	2
16	20246060	Yulianus Chandra Setyawan Margana	C	2
17	20246014	Chatarina Claudia Marisca Mega	C	2
18	20246027	Emeraldo Wahid Budi Santoso	C	2
19	20242017	Floryanus Prisca Denista Calvin	C	2
20	20246004	Amrizal Asyawal Atsal	C	2
21	20242029	Jassen Kristanto	C	3
22	20246061	Zhevanya Lauditra Adi Nugroho	C	3
23	20242019	Fx Dhenny Prihantoro	C	3
24	20242024	Hanif Aprillian	C	3
25	20246028	Fauziah Putri Rosyida	C	3
26	20246016	Constantinus Alfon Hendarwanto	C	3
27	20242001	Ahmad Arif Budijatmiko	C	3
28	20246055	Rafael Rakanaya Haryo Raditya	C	3
29	20242022	Gibran Yogananda	C	3
30	20246050	Mikael Nayotama Ardi Nugraha	C	3
31	20246048	Michael Putra Ariadi	C	3
"""

def seed_mahasiswa():
    if not os.path.exists(DB_PATH):
        print("[-] Error: Database belum ada. Jalankan init_db.py terlebih dahulu.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    baris_data = DATA_MENTAH.strip().split('\n')
    mhs_berhasil, mhs_dilewati = 0, 0

    print("[*] Menginjeksi data mahasiswa...")
    for baris in baris_data:
        kolom = baris.split('\t')
        if len(kolom) == 5:
            no_absen = int(kolom[0].strip())
            nim, nama, kelas, rombel = kolom[1].strip(), kolom[2].strip(), kolom[3].strip(), kolom[4].strip()

            try:
                cursor.execute('''
                    INSERT INTO mahasiswa (no, nim, nama, target_kelas, target_rombel)
                    VALUES (?, ?, ?, ?, ?)
                ''', (no_absen, nim, nama, kelas, rombel))
                mhs_berhasil += 1
            except sqlite3.IntegrityError:
                mhs_dilewati += 1

    conn.commit()
    conn.close()

    print(f"[+] Selesai: {mhs_berhasil} masuk, {mhs_dilewati} dilewati (duplikat).")

if __name__ == '__main__':
    seed_mahasiswa()