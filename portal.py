import requests
import subprocess
import mysql.connector
import shlex
import time
from datetime import datetime, timedelta

# Koneksi ke database MySQL
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="meliska",
    password="meliska",
    database="repository"
)

def send_unix_user_data():
    # Membuat kursor untuk mengeksekusi perintah SQL
    cursor = mydb.cursor()

    # Mendapatkan data NIM dan password dari tabel pengguna
    query = "SELECT id, nim FROM users"
    cursor.execute(query)
    results = cursor.fetchall()

    # Mengirim data ke server menggunakan curl
    url = 'http://10.0.0.20:8181/api/add_unix_user/'
    for id, nim in results:
        data = f'nim={nim}'
        command = f'curl -X POST --data-urlencode "{data}" {url}'
        print(f"URL yang digunakan: {url}")
        print(f"Perintah curl yang dihasilkan: {' '.join(command)}")
        try:
            subprocess.run(command, shell=True, check=True)
            print("Data berhasil dikirim")
        except subprocess.CalledProcessError as e:
            print(f"Terjadi kesalahan saat mengirim data: {e}")

    # Menutup kursor
    cursor.close()

def process_template_creation():
    # Membuat kursor untuk mengeksekusi perintah SQL
    cursor = mydb.cursor()

    # Mendapatkan data inputan dari database dengan status 0
    query = "SELECT nama_template, link_template, versi FROM template WHERE status_job = '0'"
    cursor.execute(query)
    results = cursor.fetchall()

    # Mendapatkan selisih waktu dengan UTC
    utc_offset = timedelta(hours=7)

    for result in results:
        nama_template, link_template, versi = result

        # Mengubah status_job menjadi 1 di database sebelum mengirim template ke server
        update_query = "UPDATE template SET status_job = 1 WHERE nama_template = %s"
        cursor.execute(update_query, (nama_template,))
        mydb.commit()

        # URL API server
        url = "http://10.0.0.21:8080/api/create_template/"

        # Data inputan untuk membuat images
        payload = {
            'nama_template': nama_template,
            'link_template': link_template,
            'versi': versi,
        }

        # Mengirim permintaan ke API server
        response = requests.post(url, json=payload)

        # Mengecek respon dari server
        if response.status_code == 200:
            print(f"Image created for {nama_template} - {link_template} successfully.")

            # Mengubah status_job menjadi 2 dan tgl_selesai menjadi waktu saat ini di zona waktu Asia/Jakarta
            current_time = datetime.utcnow() + utc_offset
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            update_query = "UPDATE template SET status_job = 2, tgl_selesai = %s WHERE nama_template = %s"
            cursor.execute(update_query, (current_time_str, nama_template))
            mydb.commit()

            # Mengubah atribut bolehkan menjadi 1 jika status_job sudah 2
            update_query = "UPDATE template SET bolehkan = 1 WHERE status_job = 2"
            cursor.execute(update_query)
            mydb.commit()
        else:
            print(f"Image creation for {nama_template} - {link_template} failed.")

            # Mengubah status_job menjadi 3 di database jika gagal membuat template
            update_query = "UPDATE template SET status_job = 3, bolehkan = 0 WHERE nama_template = %s"
            cursor.execute(update_query, (nama_template,))
            mydb.commit()

    # Menutup kursor
    cursor.close()

def process_container_creation():
    # Membuat kursor untuk mengeksekusi perintah SQL
    cursor = mydb.cursor()

    # Mendapatkan data dari tabel kontainer dengan melakukan inner join pada tabel template dan user
    query = """
        SELECT container.id, container.id_template, container.id_user, container.port_kontainer, template.nama_template, template.default_dir, template.port, users.nim, kategori.kategori
        FROM container
        INNER JOIN template ON container.id_template = template.id
        INNER JOIN users ON container.id_user = users.id
        INNER JOIN kategori ON template.id_kategori =  kategori.id
        WHERE container.status_job = 0
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Mendapatkan selisih waktu dengan UTC
    utc_offset = timedelta(hours=7)

    # URL endpoint server
    url = 'http://10.0.0.21:8080/api/create_container/'

    # Mengirim data ke server untuk setiap baris hasil query
    for result in results:
        id, id_template, id_user, port_kontainer, nama_template, default_dir, port, nim, kategori = result

        # Data yang akan dikirim ke server
        data = {
            'id': id,
            'nama_template': nama_template,
            'port_kontainer': port_kontainer,
            'port': port,
            'default_dir': default_dir,
            'nim': nim,
            'kategori': kategori
        }

        # Mengirim permintaan POST ke server dengan data
        response = requests.post(url, json=data)

        # Memeriksa respon dari server
        if response.status_code == 200:
            print(f'Data berhasil dikirim ke server: {data}')
            
            # Mengubah status_job menjadi 2 dan tgl_selesai menjadi waktu saat ini di zona waktu Asia/Jakarta
            current_time = datetime.utcnow() + utc_offset
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            update_query = "UPDATE container SET status_job = 2, tgl_selesai = %s WHERE id = %s"
            cursor.execute(update_query, (current_time_str, id,))
            mydb.commit()

            # Mengubah atribut bolehkan menjadi 1 jika status_job sudah 2
            update_query = "UPDATE container SET bolehkan = 1, status = true WHERE status_job = 2"
            cursor.execute(update_query)
            mydb.commit()
        else:
            print(f'Terjadi kesalahan saat mengirim data ke server: {data}')
            # Mengubah status_job menjadi 3 di database jika gagal membuat template
            update_query = "UPDATE container SET status_job = 3 WHERE id = %s"
            cursor.execute(update_query, (id,))
            mydb.commit()

    # Menutup kursor
    cursor.close()

def process_container_updates():
    url = 'http://10.0.0.21:8080/api/update_bolehkan_container/'

    # Fungsi untuk membaca nilai dari database berdasarkan ID kontainer
    def read_from_database():
        # Membuat kursor untuk mengeksekusi perintah SQL
        cursor = mydb.cursor()

        # Eksekusi query untuk membaca nilai bolehkan dan id dari tabel kontainer
        query = "SELECT bolehkan, id FROM container"
        cursor.execute(query)
        results = cursor.fetchall()

        # Menutup kursor
        cursor.close()

        # Mengembalikan nilai dari database
        return results

    # Fungsi untuk mengubah status kontainer dan menyimpan perubahan ke database
    def update_and_save_to_database(id, bolehkan):
        # Mengubah nilai status berdasarkan nilai bolehkan
        if bolehkan == 0:
            status = False
        elif bolehkan == 1:
            status = True
        else:
            print(f'Nilai bolehkan tidak valid untuk ID kontainer {id}')
            return

        cursor = mydb.cursor()

        # Mengupdate nilai status kontainer berdasarkan ID kontainer
        update_query = "UPDATE container SET status = %s WHERE id = %s"
        values = (status, id)
        cursor.execute(update_query, values)
        mydb.commit()

        # Menutup kursor
        cursor.close()

        print(f'Status kontainer berhasil diperbarui untuk ID kontainer {id}')

    # Fungsi untuk mengirim nilai bolehkan dan id ke server Django
    def send_to_server(id, bolehkan):
        data = {
            'id': id,
            'bolehkan': bolehkan
        }
        response = requests.post(url, json=data)

        # Memeriksa kode status respons
        if response.status_code == 200:
            print('Nilai berhasil dikirim ke server')
        else:
            print('Gagal mengirim nilai ke server')
            
    def process_updates():
        data_kontainer = read_from_database()
        for bolehkan, id in data_kontainer:
            update_and_save_to_database(id, bolehkan)
            send_to_server(id, bolehkan)
    # Memulai pertama kali menjalankan process_updates
    process_updates()
           
def delete_container():
    # URL endpoint server
    url = 'http://10.0.0.21:8080/api/delete_kontainer/'
  
    # Membuat kursor untuk mengeksekusi perintah SQL
    cursor = mydb.cursor()

    # Eksekusi query untuk membaca id dari tabel kontainer
    query = "SELECT id FROM container"
    cursor.execute(query)
    id_kontainer = cursor.fetchall()

    # Menutup kursor
    cursor.close()

    # Mengirim id ke server
    for id in id_kontainer:
        data = {
            'id': id
        }
        response = requests.post(url, json=data)

        # Memeriksa kode status respons
        if response.status_code == 200:
            print(f'Kontainer {id} berhasil dikirim ke server')
        else:
            print(f'Gagal mengirim Kontainer {id} ke server')

while True:
    send_unix_user_data()
    process_template_creation()
    process_container_creation()
    process_container_updates()
    delete_container()
    time.sleep(60)  # Jeda 1 menit
