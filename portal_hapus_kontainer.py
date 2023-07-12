import requests
import mysql.connector

url = 'http://10.0.0.21:8080/api/delete_kontainer/'

def send_kontainer_names_to_server():
    # Koneksi ke database
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="meliska",
        password="meliska",
        database="repository"
    )
    cursor = conn.cursor()

    # Eksekusi query untuk membaca id dari tabel kontainer
    query = "SELECT id FROM kontainer"
    cursor.execute(query)
    id_kontainer = cursor.fetchall()

    # Menutup koneksi database
    cursor.close()
    conn.close()

    # Mengirim id ke server
    for id in id_kontainer:
        data = {
            'id': id
        }
        response = requests.post(url, json=data)

        # Memeriksa kode status respons
        if response.status_code == 200:
            print(f'Nama template {id} berhasil dikirim ke server')
        else:
            print(f'Gagal mengirim nama template {id} ke server')

# Contoh pemanggilan fungsi
send_kontainer_names_to_server()
