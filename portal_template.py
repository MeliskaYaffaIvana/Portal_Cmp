import requests
import mysql.connector

# Koneksi ke database MySQL
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='meliska',
    password='meliska',
    database='repository'
)
cursor = conn.cursor()

# Mendapatkan data inputan dari database
query = "SELECT nama_template, link_template FROM template WHERE status = '0'"
cursor.execute(query)
results = cursor.fetchall()

for result in results:
    nama_template, link_template= result

    # URL API server
    url = "//http:10.0.0.21:8000/api/create_template/"

    # Data inputan untuk membuat images
    payload = {
        'nama_template': nama_template,
        'link_template': link_template,
    }

    # Mengirim permintaan ke API server
    response = requests.post(url, json=payload)

    # Mengecek respon dari server
    if response.status_code == 200:
        print(f"Image created for {nama_template} - {link_template} successfully.")
    else:
        print(f"Image creation for {nama_template} - {link_template} failed.")

# Tutup koneksi database
cursor.close()
conn.close()
