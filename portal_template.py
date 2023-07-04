import requests
import mysql.connector
from datetime import datetime

# Koneksi ke database MySQL
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='meliska',
    password='meliska',
    database='repository'
)
cursor = conn.cursor()

# Mendapatkan data inputan dari database
query = "SELECT nama_template, link_template,versi FROM template WHERE status_job = '0'"
cursor.execute(query)
results = cursor.fetchall()

for result in results:
    nama_template, link_template, versi = result

    # URL API server
    url = "http://10.0.0.21:8000/api/create_template/"

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

        # Mengubah status_job menjadi 1 di database setelah images berhasil dikirim ke server
        update_query = "UPDATE template SET status_job = 1 WHERE nama_template = %s"
        cursor.execute(update_query, (nama_template,))
        conn.commit()

        # Mengubah status_job menjadi 2 dan tgl_selesai menjadi waktu saat ini di database setelah server berhasil membuat template
        update_query = "UPDATE template SET status_job = 2, tgl_selesai = %s WHERE nama_template = %s"
        current_time = datetime.now('Asia/Jakarta).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(update_query, (current_time, nama_template))
        conn.commit()
    else:
        print(f"Image creation for {nama_template} - {link_template} failed.")

        # Mengubah status_job menjadi 3 di database jika gagal membuat template
        update_query = "UPDATE template SET status_job = 3 WHERE nama_template = %s"
        cursor.execute(update_query, (nama_template,))
        conn.commit()

# Tutup koneksi database
cursor.close()
conn.close()




# import requests
# import mysql.connector

# # Koneksi ke database MySQL
# conn = mysql.connector.connect(
#     host='127.0.0.1',
#     user='meliska',
#     password='meliska',
#     database='repository'
# )
# cursor = conn.cursor()

# # Mendapatkan data inputan dari database
# query = "SELECT nama_template, link_template,versi FROM template WHERE status_job = '0'"
# cursor.execute(query)
# results = cursor.fetchall()

# for result in results:
#     nama_template, link_template, versi = result
#     # print(nama_template)
#     # print(link_template)

#     # URL API server
#     url = "http://10.0.0.21:8000/api/create_template/"

   
#     # Data inputan untuk membuat images
#     payload = {
#         'nama_template': nama_template,
#         'link_template': link_template,
#         'versi': versi,
#     }

#     # Mengirim permintaan ke API server
#     response = requests.post(url, json=payload)

#     # Mengecek respon dari server
#     if response.status_code == 200:
#         print(f"Image created for {nama_template} - {link_template} successfully.")

#         # Mengubah status_job menjadi 1 di database setelah images berhasil dibuat
#         update_query = "UPDATE template SET status_job = 1 WHERE nama_template = %s"
#         cursor.execute(update_query, (nama_template,))
#         conn.commit()
#     else:
#         print(f"Image creation for {nama_template} - {link_template} failed.")

# # Tutup koneksi database
# cursor.close()
# conn.close()
