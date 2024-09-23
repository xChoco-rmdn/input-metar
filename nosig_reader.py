import re

class MetarReader:
    """Parser for METAR data"""
    def __init__(self, metar_code):
        self.metar_code = metar_code
        self.parsed_metar = {}

    def parse(self):
        self.read_time()
        self.read_wind()
        self.read_visibility()
        self.read_temperature()
        self.read_pressure()
        self.read_clouds()  # Method to parse clouds and handle height conversion
        self.read_trend()
        return self.parsed_metar

    def read_time(self):
        time_regex = r'(\d{2})(\d{2})(\d{2})Z'
        time_match = re.search(time_regex, self.metar_code)
        if time_match:
            day, hour, minute = time_match.groups()
            self.parsed_metar['day'] = day
            self.parsed_metar['hour'] = hour
            self.parsed_metar['minute'] = minute

    def read_wind(self):
        wind_regex = r'(\d{3}|VRB)(\d{2,3})KT'
        wind_match = re.search(wind_regex, self.metar_code)
        if wind_match:
            self.parsed_metar['wind_direction'] = wind_match.group(1)
            self.parsed_metar['wind_speed'] = wind_match.group(2)

    def read_visibility(self):
        visibility_regex = r'(\d{4})'
        visibility_match = re.search(visibility_regex, self.metar_code)
        if visibility_match:
            self.parsed_metar['visibility'] = visibility_match.group(1)

    def read_temperature(self):
        temp_regex = r'(\d{2})/(\d{2})'
        temp_match = re.search(temp_regex, self.metar_code)
        if temp_match:
            self.parsed_metar['temperature'] = temp_match.group(1)
            self.parsed_metar['dew_point'] = temp_match.group(2)

    def read_pressure(self):
        pressure_regex = r'Q(\d{4})'
        pressure_match = re.search(pressure_regex, self.metar_code)
        if pressure_match:
            self.parsed_metar['pressure'] = pressure_match.group(1)

    def read_trend(self):
        trend_regex = r'(NOSIG|BECMG|TEMPO)'
        trend_match = re.search(trend_regex, self.metar_code)
        if trend_match:
            self.parsed_metar['trend'] = trend_match.group(1)

    def read_clouds(self):
        # Extracting cloud type and cloud subtype, converting height into thousands of feet
        cloud_regex = r'(FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?'
        cloud_matches = re.findall(cloud_regex, self.metar_code)
        if cloud_matches:
            clouds = []
            for cloud_type, cloud_height, cloud_subtype in cloud_matches:
                # Convert cloud height to thousands of feet (e.g., 018 -> 1800 feet)
                height_in_feet = int(cloud_height) * 100
                clouds.append({
                    'cloud_type': cloud_type,
                    'cloud_height': height_in_feet,
                    'cloud_subtype': cloud_subtype if cloud_subtype else None
                })
            self.parsed_metar['clouds'] = clouds
