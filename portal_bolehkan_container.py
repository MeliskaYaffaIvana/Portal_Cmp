import time
import requests
import mysql.connector

url = 'http://10.0.0.21:8080/api/update_bolehkan_container/'

# Fungsi untuk membaca nilai dari database berdasarkan ID kontainer
def read_from_database():
    # Koneksi ke database
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="meliska",
        password="meliska",
        database="repository"
    )
    cursor = conn.cursor()

    # Eksekusi query untuk membaca nilai bolehkan dan id dari tabel kontainer
    query = "SELECT bolehkan, id FROM container"
    cursor.execute(query)
    results = cursor.fetchall()

    # Menutup koneksi database
    cursor.close()
    conn.close()

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

    # Menyimpan perubahan status kontainer ke database
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="meliska",
        password="meliska",
        database="repository"
    )
    cursor = conn.cursor()

    # Mengupdate nilai status kontainer berdasarkan ID kontainer
    update_query = "UPDATE container SET status = %s WHERE id = %s"
    values = (status, id)
    cursor.execute(update_query, values)
    conn.commit()

    # Menutup koneksi database
    cursor.close()
    conn.close()

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

# Contoh pemanggilan fungsi
data_kontainer = read_from_database()
for bolehkan, id in data_kontainer:
    update_and_save_to_database(id, bolehkan)
    send_to_server(id, bolehkan)
    time.sleep(2)  # Jeda 2 detik antara pengiriman setiap kontainer
