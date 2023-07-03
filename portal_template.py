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
query = "SELECT nama_template, link_template,versi FROM template WHERE status_job = '0'"
cursor.execute(query)
results = cursor.fetchall()

for result in results:
    nama_template, link_template, versi = result
    print(nama_template)
    print(link_template)

    # URL API server
    url = "http://10.0.0.21:8000/api/create_template/"

   
    # Data inputan untuk membuat images
    payload = {
        'nama_template': nama_template,
        'link_template': link_template,
        'versi': versi,
    }
    print(payload)
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
# query = "SELECT id, nama_template, link_template FROM template WHERE status_job = '0'"
# cursor.execute(query)
# results = cursor.fetchall()

# for result in results:
#     id, nama_template, link_template = result

#     # URL API server
#     url = "http://10.0.0.21:8000/api/create_template/"
    
#     # Data inputan untuk membuat images
#     payload = {
#         'nama_template': nama_template,
#         'link_template': link_template,
#     }

#     # Mengirim permintaan ke API server
#     response = requests.post(url, json=payload)

#     # Mengecek respon dari server
#     if response.status_code == 200:
#         print(f"Image created for {nama_template} - {link_template} successfully.")

#         # Mengubah status_job menjadi 1 di database
#         update_query = "UPDATE template SET status_job = '1' WHERE id = %s"
#         cursor.execute(update_query, (id,))
#         conn.commit()

#         print(f"Status job updated for {nama_template}")
#     else:
#         print(f"Image creation for {nama_template} - {link_template} failed.")

# # Tutup koneksi database
# cursor.close()
# conn.close()
