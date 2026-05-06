from datetime import datetime, timedelta
import ephem
import math
import swisseph as swe

# Set ephemeris path for offline calculations
swe.set_ephe_path("./assets")

def get_sun_moon_positions(datetime_obj, latitude, longitude, timezone_offset_hours=5.5):
    """
    Calculate sidereal (Nirayana) positions using Swisseph.
    The input datetime is local civil time. Convert it to UTC before passing to Swisseph.
    """
    # Convert local time to UTC for Swisseph
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    utc_dt = datetime_obj - timedelta(hours=timezone_offset_hours)
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour
    minute = utc_dt.minute
    second = utc_dt.second
    
    jd = swe.utc_to_jd(year, month, day, hour, minute, second)[0]
    
    # Calculate Sun position (sidereal with Lahiri ayanamsa)
    res_s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL + swe.FLG_SPEED)
    sun_sidereal_long = res_s[0]
    
    # Calculate Moon position (sidereal with Lahiri ayanamsa)
    res_m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL + swe.FLG_SPEED)
    moon_sidereal_long = res_m[0]
    
    # Get ayanamsa value
    ayanamsa_val = swe.get_ayanamsa(jd)

    return {
        "sun_longitude": sun_sidereal_long,
        "moon_longitude": moon_sidereal_long,
        "ayanamsa": ayanamsa_val
    }


def get_sunrise_sunset_times(date_obj, latitude, longitude):
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    obs.date = ephem.Date(date_obj.strftime('%Y/%m/%d 00:00:00'))

    sun = ephem.Sun()
    sunrise = ephem.localtime(obs.next_rising(sun))
    obs.date = ephem.Date(date_obj.strftime('%Y/%m/%d 00:00:00'))
    sunset = ephem.localtime(obs.next_setting(sun))

    if sunset < sunrise:
        obs.date = ephem.Date(sunrise)
        sunset = ephem.localtime(obs.next_setting(sun))

    return sunrise, sunset


def get_moonrise_moonset_times(date_obj, latitude, longitude):
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    obs.date = ephem.Date(date_obj.strftime('%Y/%m/%d 00:00:00'))

    moon = ephem.Moon()
    moonrise = ephem.localtime(obs.next_rising(moon))
    obs.date = ephem.Date(date_obj.strftime('%Y/%m/%d 00:00:00'))
    moonset = ephem.localtime(obs.next_setting(moon))

    if moonset < moonrise:
        obs.date = ephem.Date(moonrise)
        moonset = ephem.localtime(obs.next_setting(moon))

    return moonrise, moonset


def get_rahu_kaal(sunrise, sunset, weekday):
    segment = (sunset - sunrise) / 8
    weekday_index = {
        0: 1,  # Monday -> second segment
        1: 6,  # Tuesday -> seventh segment
        2: 4,  # Wednesday -> fifth segment
        3: 5,  # Thursday -> sixth segment
        4: 3,  # Friday -> fourth segment
        5: 2,  # Saturday -> third segment
        6: 7   # Sunday -> eighth segment
    }.get(weekday, 1)
    start = sunrise + segment * weekday_index
    end = start + segment
    return start, end


def format_time(datetime_obj):
    return datetime_obj.strftime('%H:%M')

def get_tithi(sun_long, moon_long):
    # 1. Calculate separation
    diff = (moon_long - sun_long) % 360
    
    # 2. Get the Tithi index (1 to 30)
    # Adding 1 makes it more human-readable (1-30 instead of 0-29)
    total_index = int(diff / 12) + 1
    
    # 3. Traditional names for 1 through 15
    names = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Full/New Moon"
    ]
    
    if total_index <= 15:
        paksha = "Shukla"
        tithi_in_paksha = total_index
        # If it's the 15th, it's Pournami
        name = "Pournami" if total_index == 15 else names[total_index - 1]
    else:
        paksha = "Krishna"
        tithi_in_paksha = total_index - 15
        # If it's the 30th (15th of Krishna), it's Amavasya
        name = "Amavasya" if tithi_in_paksha == 15 else names[tithi_in_paksha - 1]
        
    return {
        "number": tithi_in_paksha, # 1-15
        "name": name,              # Sanskrit Name
        "paksha": paksha,          # Shukla/Krishna
        "total_index": total_index  # 1-30 (useful for internal logic)
    }

def get_nakshatra(moon_long):
    # Total segments
    total_segments = moon_long * 27 / 360
    
    # Current Nakshatra index (0-26)
    nak_idx = int(total_segments) % 27
    
    # Calculate Pada (1, 2, 3, or 4)
    # The decimal part of total_segments tells us how far into the current Nakshatra we are
    pada = int((total_segments - int(total_segments)) * 4) + 1

    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
        "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
        "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
        "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    return {
        "number": nak_idx + 1,
        "name": nakshatras[nak_idx],
        "pada": pada,
        "display": f"{nakshatras[nak_idx]}" # e.g., "Rohini"
    }

def get_zodiac_sign(sidereal_longitude):
    """
    Get rashi (zodiac sign) from sidereal longitude.
    12 rashis × 30° each
    """
    rashi_num = int(sidereal_longitude / 30)

    rashis = [
        "Mesha", "Vrishabha", "Mithuna",
        "Kataka", "Simha", "Kanya",
        "Tula", "Vrischika", "Dhanus",
        "Makara", "Kumbha", "Meena"
    ]

    return {
        "number": rashi_num + 1,
        "name": rashis[rashi_num]
    }

def get_ayana(sun_sidereal_longitude):
    """
    Determine whether Sun is in Uttarayana or Dakshinayana.
    Uttarayana: Sun moving north (Makara to Mithuna: 270-90°)
    Dakshinayana: Sun moving south (Kataka to Dhanus: 90-270°)
    """
    if (sun_sidereal_longitude >= 270) or (sun_sidereal_longitude < 90):
        return "Uttarayana"
    else:
        return "Dakshinayana"

def get_ritu(sun_sidereal_longitude):
    """
    Calculate Ritu (6 seasons) based on Sun's position.
    Each ritu = 60° (2 months)
    """
    ritus = [
        "Vasanta", "Grishma", "Varsha",
        "Sharad", "Hemanta", "Shishira"
    ]

    ritu_num = int(sun_sidereal_longitude / 60)

    return ritus[ritu_num % 6]


def get_malayalam_tithi(name, paksha, is_adhika=False):
    malayalam_names = {
        "Pratipada": "പ്രതിപദ",
        "Dwitiya": "ദ്വിതീയ",
        "Tritiya": "ത്രിതീയ",
        "Chaturthi": "ചതുര്‍ത്തി",
        "Panchami": "പഞ്ചമി",
        "Shashthi": "ഷഷ്ടി",
        "Saptami": "സപ്തമി",
        "Ashtami": "അഷ്ടമി",
        "Navami": "നവമി",
        "Dashami": "ദശമി",
        "Ekadashi": "ഏകാദശി",
        "Dwadashi": "ദ്വാദശി",
        "Trayodashi": "ത്രയോദശി",
        "Chaturdashi": "ചതുര്ദശി",
        "Pournami": "ഔർണ്ണമി",
        "Amavasya": "അമാവാസ്യ"
    }
    paksha_ml = "ശുക്ല" if paksha == "Shukla" else "കൃഷ്ണ"
    adhika_prefix = "അധിക " if is_adhika else ""
    malayalam_name = malayalam_names.get(name, name)
    return f"{adhika_prefix}{paksha_ml} {malayalam_name}"


def get_malayalam_nakshatra(name):
    malayalam_nakshatras = {
        "Ashwini": "അശ്വിനി",
        "Bharani": "ഭരണി",
        "Krittika": "കൃത്രിക",
        "Rohini": "രോഹിണി",
        "Mrigashirsha": "മൃഗശിര",
        "Ardra": "അർദ്ര",
        "Punarvasu": "പുനർവസു",
        "Pushya": "പുഷ്യ",
        "Ashlesha": "ആശ്ലേഷ",
        "Magha": "മഘ",
        "Purva Phalguni": "പൂർവ ഫാല്ഗുണി",
        "Uttara Phalguni": "ഉത്തര ഫാല്ഗുണി",
        "Hasta": "ഹസ്ത",
        "Chitra": "ചിത്ര",
        "Swati": "സ്വാതി",
        "Vishakha": "വിശാഖ",
        "Anuradha": "അനുരാധ",
        "Jyeshtha": "ജ്യേഷ്ഠ",
        "Mula": "മുല",
        "Purva Ashadha": "പൂർവ ആശാഢ",
        "Uttara Ashadha": "ഉത്തര ആശാഢ",
        "Shravana": "ശ്രവണം",
        "Dhanishta": "ധനിഷ്ഠ",
        "Shatabhisha": "ശതഭിഷ",
        "Purva Bhadrapada": "പൂർവ ഭദ്രപദ",
        "Uttara Bhadrapada": "ഉത്തര ഭദ്രപദ",
        "Revati": "രേവതി"
    }
    return malayalam_nakshatras.get(name, name)


def get_malayalam_masu(name):
    malayalam_months = {
        "Chaitra": "ചൈത്രം",
        "Vaishakha": "വൈശാഖം",
        "Jyeshtha": "ജ്യേഷ്ഠം",
        "Ashadha": "ആഷാഢം",
        "Shravana": "ശ്രാവണം",
        "Bhadrapada": "ഭാദ്രപതം",
        "Ashwin": "ആശ്വയം",
        "Kartika": "കാർത്ഥികം",
        "Margashirsha": "മാർഗശീഷ",
        "Pausha": "പൗഷം",
        "Magha": "മഘം",
        "Phalguna": "ഫൽഗുണം"
    }
    return malayalam_months.get(name, name)


def get_malayalam_rashi(name):
    malayalam_rashis = {
        "Mesha": "മേടം",
        "Vrishabha": "വൃഷഭം",
        "Mithuna": "മിഥുനം",
        "Kataka": "കർക്കിടകം",
        "Simha": "സിംഹം",
        "Kanya": "കന്നി",
        "Tula": "തുലാം",
        "Vrischika": "വൃശ്ചികം",
        "Dhanus": "ധനുസ്",
        "Makara": "മകരം",
        "Kumbha": "കുംഭം",
        "Meena": "മീനം"
    }
    return malayalam_rashis.get(name, name)


def get_malayalam_ayana(name):
    if name == "Uttarayana":
        return "ഉത്തരായണം"
    return "ദക്ഷിണായണം"


def get_malayalam_ritu(name):
    malayalam_ritus = {
        "Vasanta": "വസന്തം",
        "Grishma": "ഗൃഷ്മം",
        "Varsha": "വർഷം",
        "Sharad": "ശരത്കാലം",
        "Hemanta": "ഹേമന്തം",
        "Shishira": "ശിശിരം"
    }
    return malayalam_ritus.get(name, name)


def get_malayalam_samvatsara(name):
    malayalam_samvatsaras = {
        "Prabhava": "പ്രഭവ",
        "Vibhava": "വിഭവ",
        "Shukla": "ശുക്ല",
        "Pramoda": "പ്രമോദ",
        "Prajapati": "പ്രജാപതി",
        "Angirasa": "അംഗിരസ്",
        "Shrimukha": "ശ്രീമുഖ",
        "Bhava": "ഭവ",
        "Yuvan": "യുവ",
        "Dhata": "ധാത്രി",
        "Isvara": "ഇശ്വര",
        "Bahudhanya": "ബഹുധാന്യ",
        "Pramathi": "പ്രമഥി",
        "Vikrama": "വിക്രമ",
        "Vrisha": "വൃഷ",
        "Chitrabhanu": "ചിത്രഭാനു",
        "Subhanu": "സുഭാനു",
        "Tarana": "തരണ",
        "Parthiva": "പർത്ഥിവ",
        "Vyaya": "വ്യയ",
        "Sarvajit": "സർവ്വജിത്",
        "Sarvadharin": "സർവ്വധാരി",
        "Virodhi": "വിരോധി",
        "Vikrita": "വിക്രിതി",
        "Khara": "ഖര",
        "Nandana": "നന്ദന",
        "Vijaya": "വിജയ",
        "Jaya": "ജയ",
        "Manmatha": "മന്മഥ",
        "Durmukhi": "ദുർമുഖ",
        "Hevilambi": "ഹേമലംബി",
        "Vilambi": "വിലംബി",
        "Vikarin": "വികാരി",
        "Sharvari": "ശർവ്വരി",
        "Plava": "പ്ലവ",
        "Shubhakrit": "ശുഭക്രിത്",
        "Sobhakrit": "ശോഭന",
        "Krodhi": "ക്രോധി",
        "Visvavasu": "വിശ്വവാസു",
        "Parabhava": "പരഭവ",
        "Plavanga": "പ്ലവംഗ",
        "Keelaka": "കിലക",
        "Saumya": "സൌമ്യ",
        "Sadharana": "സാധാരണ",
        "Virodhakrit": "വിരോധക്രിത്",
        "Paridhavi": "പരിധാവി",
        "Pramadichha": "പ്രമദിച",
        "Ananda": "ആനന്ദ",
        "Rakshasa": "രക്ഷസ",
        "Nala": "നല",
        "Pingala": "പിംഗല",
        "Kalayukti": "കലയുക്ത",
        "Siddharthi": "സിദ്ധാർത്ഥി",
        "Raudri": "റൌദ്രി",
        "Durmati": "ദുർമതി",
        "Dundubhi": "ദുണ്ഡുഭി",
        "Rudhirodgari": "രുധിരോദ്ഗാരി",
        "Raktakshaya": "രക്താക്ഷി",
        "Krodhana": "ക്രോധന",
        "Akshaya": "ക്ഷയ"
    }
    return malayalam_samvatsaras.get(name, name)


def get_tithi_at_sunrise(date_obj, latitude, longitude):
    reference_time = datetime(date_obj.year, date_obj.month, date_obj.day, 12, 0, 0)
    sunrise_time = get_sunrise_time(reference_time, latitude, longitude)
    positions = get_sun_moon_positions(sunrise_time, latitude, longitude)
    return get_tithi(positions['sun_longitude'], positions['moon_longitude'])


def get_lunar_month(sun_long, moon_long):
    """
    Determine lunar month based on Sun and Moon positions at the last New Moon.
    """
    months = [
        "Chaitra", "Vaishakha", "Jyeshtha",
        "Ashadha", "Shravana", "Bhadrapada",
        "Ashwin", "Kartika", "Margashirsha",
        "Pausha", "Magha", "Phalguna"
    ]
    
    # Nakshatra to month mapping (0-indexed nakshatras to 0-indexed months)
    # Based on: Chaitra starts at Chitra (13), each month ~2.25 nakshatras
    nakshatra_to_month = [
        7,   # 0: Aswini -> Kartika
        7,   # 1: Bharani -> Kartika
        8,   # 2: Krittika -> Margashirsha
        8,   # 3: Rohini -> Margashirsha
        9,   # 4: Mrigashirsha -> Pausha
        9,   # 5: Ardra -> Pausha
        10,  # 6: Punarvasu -> Magha
        10,  # 7: Pushya -> Magha
        11,  # 8: Aslesha -> Phalguna
        11,  # 9: Magha -> Phalguna
        0,   # 10: Purva Phalguni -> Chaitra
        0,   # 11: Uttara Phalguni -> Chaitra
        0,   # 12: Hasta -> Chaitra
        0,   # 13: Chitra -> Chaitra
        0,   # 14: Swati -> Chaitra
        1,   # 15: Visakha -> Vaishakha
        1,   # 16: Anuradha -> Vaishakha
        1,   # 17: Jyeshtha -> Vaishakha
        1,   # 18: Mula -> Vaishakha
        2,   # 19: Purva Ashadha -> Jyeshtha
        2,   # 20: Uttara Ashadha -> Jyeshtha
        3,   # 21: Shravana -> Ashadha
        3,   # 22: Dhanishta -> Ashadha
        3,   # 23: Shatabhisha -> Ashadha
        4,   # 24: Purva Bhadrapada -> Shravana
        4,   # 25: Uttara Bhadrapada -> Shravana
        5,   # 26: Revati -> Bhadrapada
    ]
    
    nak_num = int(moon_long * 27 / 360) % 27
    month_num = nakshatra_to_month[nak_num]
    
    return months[month_num]


def get_panchangam_for_date(date_obj, latitude=8.5241, longitude=76.9366):
    """Return a Panchangam summary for a given date and location."""
    if isinstance(date_obj, datetime):
        target_date = date_obj.date()
    else:
        target_date = date_obj

    reference_time = datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0)
    sunrise_time, sunset_time = get_sunrise_sunset_times(reference_time, latitude, longitude)
    positions = get_sun_moon_positions(sunrise_time, latitude, longitude)
    sun_long = positions['sun_longitude']
    moon_long = positions['moon_longitude']

    tithi = get_tithi(sun_long, moon_long)
    previous_tithi = get_tithi_at_sunrise(target_date - timedelta(days=1), latitude, longitude)
    is_adhika = (
        previous_tithi['paksha'] == tithi['paksha'] and
        previous_tithi['name'] == tithi['name']
    )

    nakshatra = get_nakshatra(moon_long)
    zodiac = get_zodiac_sign(sun_long)
    ayana = get_ayana(sun_long)
    ritu = get_ritu(sun_long)
    lunar_month = get_lunar_month(sun_long, moon_long)
    samvatsara = get_samvatsara(target_date)
    day = get_day_of_week(target_date)

    moonrise_time, moonset_time = get_moonrise_moonset_times(reference_time, latitude, longitude)
    rahu_start, rahu_end = get_rahu_kaal(sunrise_time, sunset_time, target_date.weekday())
    rahu_kaal = f"{format_time(rahu_start)} - {format_time(rahu_end)}"

    tithi_label = f"{'Adhika ' if is_adhika else ''}{tithi['paksha']} {tithi['name']}"

    return {
        'date': target_date.strftime('%d-%m-%Y'),
        'sunrise': sunrise_time.strftime('%H:%M:%S'),
        'sunset': sunset_time.strftime('%H:%M:%S'),
        'moonrise': moonrise_time.strftime('%H:%M:%S'),
        'moonset': moonset_time.strftime('%H:%M:%S'),
        'rahu_kaal': rahu_kaal,
        'tithi': tithi_label,
        'tithi_ml': get_malayalam_tithi(tithi['name'], tithi['paksha'], is_adhika),
        'nakshatra': nakshatra['display'],
        'nakshatra_ml': get_malayalam_nakshatra(nakshatra['name']),
        'masu': zodiac['name'],
        'masu_ml': get_malayalam_rashi(zodiac['name']),
        'ayana': ayana,
        'ayana_ml': get_malayalam_ayana(ayana),
        'ritu': ritu,
        'ritu_ml': get_malayalam_ritu(ritu),
        'lunar_month': lunar_month,
        'lunar_month_ml': get_malayalam_masu(lunar_month),
        'samvatsara': samvatsara,
        'samvatsara_ml': get_malayalam_samvatsara(samvatsara),
        'day': day,
        'latitude': latitude,
        'longitude': longitude,
    }

def get_samvatsara(datetime_obj):
    """
    Get Samvatsara (60-year cycle) from Hindu lunar year.
    The Hindu year starts on Chaitra Shukla Pratipada (around mid-April).
    Anchor: Chaitra 1, 2025 (April 13, 2025) = Visvavasu (index 38)
    """
    samvatsaras = [
        "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati",
        "Angirasa", "Shrimukha", "Bhava", "Yuvan", "Dhata",
        "Isvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha",
        "Chitrabhanu", "Subhanu", "Tarana", "Parthiva", "Vyaya",
        "Sarvajit", "Sarvadharin", "Virodhi", "Vikrita", "Khara",
        "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi",
        "Hevilambi", "Vilambi", "Vikarin", "Sharvari", "Plava",
        "Shubhakrit", "Sobhakrit", "Krodhi", "Visvavasu", "Parabhava",
        "Plavanga", "Keelaka", "Saumya", "Sadharana", "Virodhakrit",
        "Paridhavi", "Pramadichha", "Ananda", "Rakshasa", "Nala",
        "Pingala", "Kalayukti", "Siddharthi", "Raudri", "Durmati",
        "Dundubhi", "Rudhirodgari", "Raktakshaya", "Krodhana", "Akshaya"
    ]

    # Chaitra Shukla Pratipada occurs around mid-April
    # Approximate date for 2025: April 13
    # If date is before mid-April, it's still in the previous Hindu year
    if datetime_obj.month < 4 or (datetime_obj.month == 4 and datetime_obj.day < 13):
        hindu_year = datetime_obj.year - 1
    else:
        hindu_year = datetime_obj.year
    
    # Base year 2025 (Chaitra 1, 2025) = index 38
    idx = (38 + hindu_year - 2025) % 60
    return samvatsaras[idx]

def get_day_of_week(datetime_obj):
    """
    Get day of week name.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
    return days[datetime_obj.weekday()]

def get_sunrise_time(date_obj, latitude, longitude):
    """
    Calculate the sunrise time for the current panchangam day.
    If the current time is before today's sunrise, returns yesterday's sunrise.
    """
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    
    # Use the local date's midnight as the reference point
    obs.date = ephem.Date(date_obj.strftime('%Y/%m/%d 00:00:00'))
    today_sunrise = ephem.localtime(obs.next_rising(ephem.Sun()))

    if date_obj < today_sunrise:
        # Current time is before today's sunrise, so the current panchangam day
        # began at yesterday's sunrise.
        sunrise_datetime = ephem.localtime(obs.previous_rising(ephem.Sun()))
    else:
        sunrise_datetime = today_sunrise

    return sunrise_datetime

def main():
    # Date and time: May 6, 2026, 12:01 (current time for display)
    current_time = datetime(2026, 5, 6, 12, 1)
    # Location: Kerala, India (approx Thiruvananthapuram)
    latitude = 8.5241
    longitude = 76.9366

    # Use the shared panchangam helper for output
    data = get_panchangam_for_date(current_time, latitude, longitude)

    print("GSB Panchang")
    print(f"Date: {data['date']} ({data['day']})")
    print(f"Sunrise: {data['sunrise']}")
    print(f"Sunset: {data['sunset']}")
    print(f"Moonrise: {data['moonrise']}")
    print(f"Moonset: {data['moonset']}")
    print(f"Rahu Kaal: {data['rahu_kaal']}")
    print()
    print(f"Masu/month: {data['masu']} / മലയാളം: {data['masu_ml']}")
    print(f"Lunar Month: {data['lunar_month']} / മലയാളം: {data['lunar_month_ml']}")
    print(f"Samvatsara: {data['samvatsara']}")
    print()
    print(f"Tithi: {data['tithi']} / മലയാളം: {data['tithi_ml']}")
    print(f"Nakshatra: {data['nakshatra']} / മലയാളം: {data['nakshatra_ml']}")
    print(f"Ayana: {data['ayana']} / മലയാളം: {data['ayana_ml']}")
    print(f"Ritu: {data['ritu']} / മലയാളം: {data['ritu_ml']}")

if __name__ == "__main__":
    main()