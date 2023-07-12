import requests
import mysql.connector

url = 'http://10.0.0.21:8181/api/delete_template/'

def send_template_names_to_server():
    # Koneksi ke database
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="meliska",
        password="meliska",
        database="repository"
    )
    cursor = conn.cursor()

    # Eksekusi query untuk membaca nama_template dari tabel template
    query = "SELECT nama_template FROM template"
    cursor.execute(query)
    template_names = cursor.fetchall()

    # Menutup koneksi database
    cursor.close()
    conn.close()

    # Mengirim nama _template ke server
    for nama_template in template_names:
        data = {
            'nama_template': nama_template
        }
        response = requests.post(url, json=data)

        # Memeriksa kode status respons
        if response.status_code == 200:
            print(f'Nama template {nama_template} berhasil dikirim ke server')
        else:
            print(f'Gagal mengirim nama template {nama_template} ke server')

# Contoh pemanggilan fungsi
send_template_names_to_server()
