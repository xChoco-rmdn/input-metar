import logging
from datetime import datetime
from browsermanager import BrowserManager
from metarreader import read_metar_code
from nosig_reader import MetarReader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_custom_date_selector(input_day: str) -> str:
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_day = datetime.now().day

    if not input_day.isdigit() or not (1 <= int(input_day) <= 31):
        raise ValueError("Invalid day. Please enter a number between 1 and 31.")

    if int(input_day) == current_day:
        custom_date_selector = f"/{input_day}/{current_year} (Today)"
    else:
        custom_date_selector = f"{current_month}/{input_day}/"

    return custom_date_selector


def handle_cloud_selection(page, cloud_type: str, cloud_subtype: str, cloud_height=None):
    cloud_oktas_mapping = {
        "FEW": "1-2 oktas",
        "SCT": "3-4 oktas",
        "BKN": "5-7 oktas",
        "OVC": "8 oktas"
    }

    okta_value = cloud_oktas_mapping.get(cloud_type)

    if not okta_value:
        logging.error("Invalid cloud type provided.")
        return
    if not cloud_subtype:
        cloud_subtype = "-"

    try:
        page.get_by_label("General").locator("#clouds-jumlah").select_option(cloud_type)
        page.get_by_label("General").locator("#cloud_height").click()
        page.get_by_label("General").locator("#cloud_height").fill(str(cloud_height))

        cloud_name = f"{cloud_type} ({okta_value}) {cloud_subtype}"
        page.get_by_role("row", name=cloud_name).get_by_role("button").click()

        logging.info(f"Cloud selection successful: {cloud_name}")

    except Exception as e:
        logging.error(f"Error during cloud selection: {e}")


def fill_form(page, user_input):
    try:

        user_input = "METAR WADS 231000Z 31008KT 9000 SCT018 29/25 Q1009 NOSIG="
        parsed_metar = read_metar_code(user_input)
        # Extract data from parsed METAR
        input_day = user_input['day']
        cloud_type = user_input['clouds'][0]['cloud_type']
        cloud_height = user_input['clouds'][0]['cloud_height']
        cloud_subtype = user_input['clouds'][0]['cloud_subtype']

        # Step 1: Kode stasiun
        logging.info("Filling station code...")
        page.wait_for_load_state("networkidle")
        page.locator("#vs2__combobox").scroll_into_view_if_needed()
        page.locator("#vs2__combobox").get_by_label("Loading...").click()
        page.get_by_role("option", name="97260").click()
        logging.info("Station code selected.")

        # Step 2: Pengamat
        logging.info("Selecting observer...")
        page.wait_for_load_state("networkidle")
        page.get_by_label("Loading...", exact=True).click()
        page.get_by_role("option", name="Zulkifli Ramadhan").click()
        logging.info("Observer selected.")

        # Step 3: Tanggal (Date)
        logging.info("Selecting date...")
        custom_date_selector = get_custom_date_selector(input_day)
        page.locator("#datepicker__value_").click()
        page.get_by_label(custom_date_selector).click()
        logging.info("Date selected.")

        # Step 4: Waktu METAR (Time)
        logging.info("Filling METAR time...")
        page.get_by_label("Jam").select_option(user_input['hour'])
        page.get_by_label("Menit").select_option(user_input['minute'])
        logging.info("Time selected.")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Step 5: Arah dan kecepatan angin (Wind direction and speed)
        logging.info("Filling wind direction and speed...")
        page.get_by_label("Arah Angin (derajat)").click()
        page.get_by_label("Arah Angin (derajat)").fill(user_input['wind_direction'])
        page.get_by_label("Kecepatan Angin (knot)").click()
        page.get_by_label("Kecepatan Angin (knot)").fill(user_input['wind_speed'])
        logging.info("Wind direction and speed filled.")

        # Step 6: Visibility
        logging.info("Filling visibility...")
        page.get_by_role("spinbutton", name="Prevailling (m) Jarak pandang").click()
        page.get_by_role("spinbutton", name="Prevailling (m) Jarak pandang").fill(user_input['visibility'])
        logging.info("Visibility filled.")

        # Step 7: Awan (Clouds)
        logging.info("Selecting cloud type and subtype...")
        handle_cloud_selection(page, cloud_type, cloud_subtype, cloud_height)
        logging.info("Cloud selection completed.")

        # Step 8: Suhu dan kelembaban (Temperature and Dew Point)
        logging.info("Filling temperature and dew point...")
        page.locator("#v-air-temp").fill(user_input['temperature'])
        page.locator("#v-dew-point").fill(user_input['dew_point'])
        logging.info("Temperature and dew point filled.")

        # Step 9: Tekanan udara (Pressure)
        logging.info("Filling air pressure...")
        page.get_by_label("TEKANAN UDARA (QNH)").fill(user_input['pressure'])
        logging.info("Air pressure filled.")

        # Step 10: Trend NOSIG
        logging.info("Selecting trend NOSIG...")
        page.get_by_role("tab", name="Trend").click()
        page.get_by_label("Trend").locator("#input-type").select_option(user_input['trend'])
        logging.info("Trend NOSIG selected.")

        # Step 11: Submit
        logging.info("Clicking preview button...")
        page.get_by_role("button", name="Preview").click()
        logging.info("Form preview completed.")
        # Uncomment to submit: page.get_by_role("button", name="Submit").click()

    except Exception as e:
        logging.error(f"Error filling form: {e}")

if __name__ == "__main__":

    # Parse the METAR using MetarReader
    metar_code = "METAR WADS 231000Z 31008KT 9000 SCT018 29/25 Q1009 NOSIG="
    parsed_metar = MetarReader(metar_code).parse()

    # Define user data directory and the target URL
    user_data_dir = "./user_data"
    url = "https://bmkgsatu.bmkg.go.id/meteorologi/metarspeci"

    # Create an instance of BrowserManager and start the browser
    manager = BrowserManager(user_data_dir=user_data_dir, headless=False)

    try:
        manager.start_browser(url)
        page = manager.page
        fill_form(page, parsed_metar)  # Pass the parsed_metar as user_input
    finally:
        manager.stop_browser()
