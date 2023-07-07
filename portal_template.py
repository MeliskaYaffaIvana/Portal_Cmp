import requests
import mysql.connector
from datetime import datetime, timedelta

# # Koneksi ke database
# conn = mysql.connector.connect(
#     host='127.0.0.1',
#     user='meliska',
#     password='meliska',
#     database='repository'
# )

# cursor = conn.cursor()

# # Mendapatkan data dari tabel kontainer dengan melakukan inner join pada tabel template dan user
# query = """
#     SELECT container.nama_kontainer, container.id_template, container.id_user, template.nama_template, template.default_dir, template.port, users.nim, kategori.kategori
#     FROM container
#     INNER JOIN template ON container.id_template = template.id
#     INNER JOIN users ON container.id_user = users.id
#     INNER JOIN kategori ON template.id_kategori =  kategori.id
# """
# cursor.execute(query)
# results = cursor.fetchall()

# # URL endpoint server
# url = 'http://10.0.0.21:8080/api/create_container/'

# # Mendapatkan selisih waktu dengan UTC
# utc_offset = timedelta(hours=7)

# # Mengirim data ke server untuk setiap baris hasil query
# for result in results:
#     nama_kontainer, id_template, id_user, nama_template, default_dir, port, nim, kategori = result

#     # Data yang akan dikirim ke server
#     data = {
#         'nama_kontainer':nama_kontainer,
#         'nama_template': nama_template,
#         'port':port,
#         'default_dir':default_dir,
#         'nim': nim,
#         'kategori': kategori
#     }

#     # Mengirim permintaan POST ke server dengan data
#     response = requests.post(url, json=data)

#     # Memeriksa respon dari server
#     if response.status_code == 200:
#         print(f'Data berhasil dikirim ke server: {data}')
#         # Mengubah status_job menjadi 2 dan tgl_selesai menjadi waktu saat ini di zona waktu Asia/Jakarta
#         current_time = datetime.utcnow() + utc_offset
#         current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
#         update_query = "UPDATE container SET status_job = 2, tgl_selesai = %s WHERE nama_kontainer = %s"
#         cursor.execute(update_query, (current_time_str, nama_kontainer))
#         conn.commit()

#         # Mengubah atribut bolehkan menjadi 1 jika status_job sudah 2
#         update_query = "UPDATE container SET bolehkan = 1 WHERE status_job = 2"
#         cursor.execute(update_query)
#         conn.commit()
#     else:
#         print(f'Terjadi kesalahan saat mengirim data ke server: {data}')
#         # Mengubah status_job menjadi 3 di database jika gagal membuat template
#         update_query = "UPDATE container SET status_job = 3 WHERE nama_kontainer = %s"
#         cursor.execute(update_query, (nama_kontainer,))
#         conn.commit()

# # Tutup koneksi database
# cursor.close()
# conn.close()

# Koneksi ke database MySQL
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='meliska',
    password='meliska',
    database='repository'
)
cursor = conn.cursor()

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
    conn.commit()

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
        conn.commit()

        # Mengubah atribut bolehkan menjadi 1 jika status_job sudah 2
        update_query = "UPDATE template SET bolehkan = 1 WHERE status_job = 2"
        cursor.execute(update_query)
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
