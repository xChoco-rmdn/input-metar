import re


class MetarReader:
    def __init__(self, metar_code):
        self.metar_code = metar_code
        self.parsed_metar = {}

    def read(self):
        self.read_type()  # Mendeteksi METAR atau SPECI
        self.read_icao()
        self.read_time()
        self.read_wind()
        self.read_visibility()
        self.read_rvr()
        self.read_weather()
        self.read_clouds()
        self.read_temperature_dew_point()
        self.read_pressure()
        self.read_trends()  # Menggunakan metode yang sama untuk trend
        return self.parsed_metar

    def read_type(self):
        """Mendeteksi apakah laporan adalah METAR atau SPECI"""
        if self.metar_code.startswith("METAR"):
            self.parsed_metar['type'] = "METAR"
        elif self.metar_code.startswith("SPECI"):
            self.parsed_metar['type'] = "SPECI"
        else:
            self.parsed_metar['type'] = "UNKNOWN"

    def read_icao(self):
        self.parsed_metar['icao'] = self.metar_code.split()[1]

    def read_time(self):
        time_regex = r'(\d{2})(\d{2})(\d{2})Z'
        time_match = re.search(time_regex, self.metar_code)
        if time_match:
            day, hour, minute = time_match.groups()
            self.parsed_metar['time'] = {
                'day': day,
                'hour': hour,
                'minute': minute
            }

    def read_wind(self, segment=None):
        if segment is None:
            segment = self.metar_code
        wind_regex = r'(\d{3}|VRB)(\d{2,3})(G\d{2,3})?KT'
        wind_match = re.search(wind_regex, segment)
        if wind_match:
            wind_dir, wind_speed, gust = wind_match.groups()
            return {
                'direction': wind_dir,
                'speed': wind_speed + ' KT',
                'gust': gust[1:] + ' KT' if gust else None
            }
        return None

    def read_visibility(self, segment=None):
        if segment is None:
            segment = self.metar_code
        vis_regex = r'(\d{4})'
        vis_match = re.search(vis_regex, segment)
        if vis_match:
            return vis_match.group(1) + ' meters'
        return None

    def read_rvr(self):
        rvr_regex = r'R(\d{2})([LRC]?)/(\d{4})([U|D|N]?)'
        rvr_matches = re.findall(rvr_regex, self.metar_code)
        if rvr_matches:
            self.parsed_metar['rvr'] = [{'runway': rwy + (rwy_side if rwy_side else ''),
                                         'range': range_ + ' meters',
                                         'trend': trend if trend else None}
                                        for rwy, rwy_side, range_, trend in rvr_matches]

    def read_weather(self, segment=None):
        if segment is None:
            segment = self.metar_code
        weather_conditions = {
            "-": "light", "+": "heavy", "VC": "nearby", "MI": "shallow", "PR": "partial",
            "BC": "patches", "DR": "low drifting", "BL": "blowing", "SH": "showers",
            "TS": "thunderstorm", "FZ": "freezing", "DZ": "drizzle", "RA": "rain",
            "SN": "snow", "SG": "snow grains", "IC": "ice crystals", "PE": "ice pellets",
            "GR": "hail", "GS": "small hail", "BR": "mist", "FG": "fog", "FU": "smoke",
            "VA": "volcanic ash", "DU": "dust", "SA": "sand", "HZ": "haze", "PO": "dust whirls",
            "SQ": "squalls", "FC": "funnel cloud", "SS": "sandstorm", "DS": "dust storm"
        }
        wx_regex = r'(-|\+|VC)?(MI|PR|BC|DR|BL|SH|TS|FZ)?(DZ|RA|SN|SG|IC|PE|GR|GS|BR|FG|FU|VA|DU|SA|HZ|PO|SQ|FC|SS|DS)'
        wx_matches = re.findall(wx_regex, segment)
        if wx_matches:
            return [' '.join([weather_conditions[part] for part in match if part])
                    for match in wx_matches]
        return None

    def read_clouds(self):
        cloud_coverage = {
            'FEW': 'few', 'SCT': 'scattered', 'BKN': 'broken', 'OVC': 'overcast', 'NSC': 'no significant clouds',
            'VV': 'vertical visibility'
        }
        cloud_regex = r'(FEW|SCT|BKN|OVC|NSC|VV)(\d{3})(CB|TCU)?'
        cloud_matches = re.findall(cloud_regex, self.metar_code)
        if cloud_matches:
            self.parsed_metar['clouds'] = [{'coverage': cloud_coverage[coverage],
                                            'height': int(height) * 100,
                                            'type': cloud_type if cloud_type else None}
                                           for coverage, height, cloud_type in cloud_matches]

    def read_temperature_dew_point(self):
        temp_dew_regex = r'M?(\d{2})/M?(\d{2})'
        temp_dew_match = re.search(temp_dew_regex, self.metar_code)
        if temp_dew_match:
            temp, dew_point = temp_dew_match.groups()
            self.parsed_metar['temperature'] = f"{'-' if 'M' in temp_dew_match.group(0) else ''}{temp}°C"
            self.parsed_metar['dew_point'] = f"{'-' if 'M' in temp_dew_match.group(0) else ''}{dew_point}°C"

    def read_pressure(self):
        pressure_regex = r'Q(\d{4})'
        pressure_match = re.search(pressure_regex, self.metar_code)
        if pressure_match:
            self.parsed_metar['pressure'] = pressure_match.group(1) + ' hPa'

    def read_trends(self):
        trend_regex = r'(TEMPO|BECMG|NOSIG|FM|TL)\s+([\dA-Z\s/]+)'
        trend_matches = re.findall(trend_regex, self.metar_code)
        if trend_matches:
            trends = []
            for trend, details in trend_matches:
                trend_data = {'trend_type': trend}

                # Parse FM and TL times
                fm_regex = r'FM(\d{2})(\d{2})'
                tl_regex = r'TL(\d{2})(\d{2})'
                fm_match = re.search(fm_regex, details)
                tl_match = re.search(tl_regex, details)

                if fm_match:
                    fm_hour, fm_minute = fm_match.groups()
                    trend_data['from'] = f"{fm_hour}:{fm_minute} UTC"
                if tl_match:
                    tl_hour, tl_minute = tl_match.groups()
                    trend_data['till'] = f"{tl_hour}:{tl_minute} UTC"

                # Parse visibility using the existing function
                trend_visibility = self.read_visibility(details)
                if trend_visibility:
                    trend_data['visibility'] = trend_visibility

                # Parse wind using the existing function
                trend_wind = self.read_wind(details)
                if trend_wind:
                    trend_data['wind'] = trend_wind

                # Parse weather using the existing function
                trend_weather = self.read_weather(details)
                if trend_weather:
                    trend_data['weather'] = trend_weather

                trends.append(trend_data)

            self.parsed_metar['trends'] = trends


# Contoh penggunaan class
metar_code = input("masukan input : ")
parser = MetarReader(metar_code)
parsed_metar = parser.read()

# Cetak hasil parsing
for key, value in parsed_metar.items():
    print(f"{key}: {value}")
