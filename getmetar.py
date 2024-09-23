import requests
import re
from datetime import datetime, timezone


class CMSSMetarFetcher:
    def __init__(self, url_cmss):
        """Inisialisasi dengan URL CMSS untuk pengambilan data METAR."""
        self.url = url_cmss
        self.data = None  # Tempat menyimpan data dari server setelah diambil

    def fetch_data(self):
        """Mengambil data dari URL dan menyimpannya dalam atribut 'data'."""
        try:
            # Mengambil data dari URL CMSS
            response = requests.get(self.url)
            if response.status_code == 200:
                self.data = response.text.strip()
                print("Data METAR berhasil diambil.")
            else:
                print(f"Error: Tidak dapat mengambil data METAR. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: Gagal mengakses URL. Detail: {e}")

    @staticmethod
    def get_metar_time_now():
        """Menghitung waktu METAR terdekat (jam penuh atau 30 menit) berdasarkan waktu sekarang."""
        now = datetime.now(timezone.utc)  # Mengambil waktu saat ini dalam UTC
        current_hour = now.strftime("%H")  # Jam saat ini
        current_minute = now.minute  # Menit saat ini

        # Jika sekarang kurang dari menit 30, gunakan jam penuh. Jika lebih dari 30, gunakan jam 30.
        if current_minute < 30:
            metar_time = f"{current_hour}00"
        else:
            metar_time = f"{current_hour}30"

        current_date = now.strftime("%d")  # Tanggal saat ini
        return f"{current_date}{metar_time}"  # Menghasilkan waktu dalam format 'ddhhmm'

    def find_metar(self, metar_time):
        """Mencari METAR berdasarkan kode stasiun WADS dan waktu METAR."""
        if not self.data:
            print("Data belum diambil. Gunakan 'fetch_data()' untuk mengambil data terlebih dahulu.")
            return None

        # Membuat pola pencarian berdasarkan waktu
        pattern = rf"SAID35 WADS {metar_time}\nMETAR WADS {metar_time}Z.*?="
        match = re.search(pattern, self.data)

        if match:
            return match.group(0)  # Mengembalikan hasil pencarian
        else:
            print(f"Tidak ditemukan data METAR untuk WADS pada waktu {metar_time}")
            return None

    def find_all_metar_today(self):
        """Mengambil semua data METAR pada hari ini berdasarkan tanggal saat ini."""
        if not self.data:
            print("Data belum diambil. Gunakan 'fetch_data()' untuk mengambil data terlebih dahulu.")
            return []

        now = datetime.now(timezone.utc)  # Mengambil waktu saat ini dalam UTC
        current_date = now.strftime("%d")  # Tanggal saat ini dalam format 2 digit (dd)

        # Mencari semua entri yang cocok dengan pola SAID35 WADS pada tanggal hari ini
        pattern = rf"SAID35 WADS {current_date}\d{{4}}\nMETAR WADS {current_date}\d{{4}}Z.*?="
        matches = re.findall(pattern, self.data)

        if matches:
            return matches  # Mengembalikan semua data METAR yang ditemukan
        else:
            print(f"Tidak ditemukan data METAR untuk WADS pada hari ini ({current_date})")
            return []

    def get_latest_metar(self):
        """Mengambil data METAR terbaru (jam penuh atau 30 menit terdekat)."""
        metar_time = self.get_metar_time_now()  # Mengambil waktu METAR terbaru
        return self.find_metar(metar_time)  # Cari dan kembalikan data METAR untuk waktu tersebut


# Penggunaan class
url = "http://172.19.1.1/cgi-bin/extract_cmss.pl"  # Ubah ini dengan URL yang valid

# Inisialisasi objek fetcher
cmss_fetcher = CMSSMetarFetcher(url)

# Mengambil data dari server
cmss_fetcher.fetch_data()

# Mengambil data METAR terbaru (jam penuh atau 30 menit terdekat)
latest_metar = cmss_fetcher.get_latest_metar()
if latest_metar:
    print(f"Data METAR terbaru:\n{latest_metar}")

# Mengambil semua METAR pada hari ini
all_metar_today = cmss_fetcher.find_all_metar_today()
if all_metar_today:
    print("\nSemua data METAR untuk hari ini:")
    for metar in all_metar_today:
        print(metar)
        print("------------------------------------------------")
