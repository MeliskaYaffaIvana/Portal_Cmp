import time
import requests
import mysql.connector

# Fungsi untuk membaca nilai dari database berdasarkan ID kontainer
def read_from_database(id_kontainer):
    # Koneksi ke database
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="meliska",
        password="meliska",
        database="repository"
    )
    cursor = conn.cursor()

    # Eksekusi query untuk membaca nilai dari database
    query = f"SELECT bolehkan FROM container WHERE id = {id}"
    cursor.execute(query)
    result = cursor.fetchone()

    # Menutup koneksi database
    cursor.close()
    conn.close()

    # Mengembalikan nilai dari database
    if result is not None:
        return result[0]
    else:
        return None

# URL endpoint dan ID kontainer yang ingin diubah
base_url = 'http://10.0.0.21:8282/api/update_bolehkan_container/'


# Fungsi untuk membaca status container dari server berdasarkan ID kontainer
def read_status_from_server(id):
    url = f"{base_url}{id}/get-bolehkan/"
    response = requests.get(url)  # Kirim permintaan GET untuk membaca status
    if response.status_code == 200:
        data = response.json()
        return data['bolehkan']
    else:
        return None

# Fungsi untuk melakukan polling dan mengirim permintaan perubahan
def poll_and_send():
    previous_bolehkan = None
    while True:
        # Kode untuk membaca nilai dari database berdasarkan ID kontainer
        bolehkan_database = read_from_database(id)

        # Membaca status container dari server berdasarkan ID kontainer
        bolehkan_server = read_status_from_server(id)

        # Membandingkan nilai status server dengan nilai status database
        if bolehkan_server is not None and bolehkan_server != bolehkan_database:
            # Data yang akan dikirim
            data = {
                'bolehkan': bolehkan_database
            }

            # Kirim permintaan PATCH
            url = f"{base_url}{id}/update-bolehkan/"
            response = requests.patch(url, json=data)

            # Periksa kode status respons
            if response.status_code == 200:
                print('Permintaan berhasil:', response.json()['message'])
            else:
                print('Permintaan gagal:', response.text)

        # Mengupdate nilai sebelumnya
        previous_bolehkan = bolehkan_database

        # Waktu jeda antara setiap polling (misalnya, 5 detik)
        time.sleep(5)  # Ganti dengan waktu jeda yang diinginkan

# Panggil fungsi polling
poll_and_send()
