''' Module for all the global constants of the app '''

MAIN_COLOR = (0, 64/255, 52/255, 1)
SECONDRY_COLOR = (16/255, 112/255, 94/255, 1)
TERNARY_COLOR = (20/255, 184/255, 154/255, 1)
CAUTION_COLOR = (230/255, 179/255, 50/255, 1)
WARNING_COLOR = (192/255, 43/255, 38/255, 1)
GREY_COLOR = (240/255, 240/255, 240/255, 1)

PRAYER_CATEGORY_NAMES = ('Group', 'Alone', 'Delayed', 'Not Prayed')
PRAYER_CATEGORY_COLORS = (SECONDRY_COLOR, TERNARY_COLOR, CAUTION_COLOR, WARNING_COLOR)
CATEGORY_COLORS_DICT = {PRAYER_CATEGORY_NAMES[i]: PRAYER_CATEGORY_COLORS[i] for i in range(4)}
PRAYER_NAMES = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")

NAVIGATION_DATA = (
					{"text": "Main Screen", "icon": "data/back.png", "screen": "dashboard"},
					{"text": "Prayer Times", "icon": "data/time.png", "screen": "prayer_times"},
					{"text": "Prayer Records", "icon": "data/record.png", "screen": "prayer_records"},
					{"text": "Prayer Graphs", "icon": "data/graph.png", "screen": "record_graphs"},
					{"text": "Calendar", "icon": "data/calendar.png", "screen": "calendar"},
					{"text": "Qibla", "icon": "data/compass.png", "screen": "qibla"},
					{"text": "Settings", "icon": "data/settings.png", "screen": "settings"}
				)

PRAYER_METHODS = (
				'Muslim World League', 'Islamic Society of North America (ISNA)',
				'Egyptian General Authority of Survey', 'Umm Al-Qura University, Makkah',
				'University of Islamic Sciences, Karachi', 'Gulf Region', 'Kuwait',
				'Qatar', 'Majlis Ugama Islam Singapura, Singapore',
				'Union Organization Islamic de France', 'Diyanet İşleri Başkanlığı, Turkey',
				'Spiritual Administration of Muslims of Russia', 'Institute of Geophysics, University of Tehran',
				'Shia Ithna-Ashari, Leva Institute, Qum'
				)

ASR_FACTORS = ("Standard", "Hanafi")
TIME_FORMATS = ("24h", "12h")
HIGH_LAT_METHODS = ("Night Middle", "Angle Based", "One Seventh")
OFFSET_MINUTES = tuple(f"{x} min" for x in range(61))

SETTINGS_OPTIONS = {"calc_method": PRAYER_METHODS, "asr_factor": ASR_FACTORS,
					"time_format": TIME_FORMATS, "high_lats": HIGH_LAT_METHODS,
					"imsak_offset": OFFSET_MINUTES, "dhuhr_offset": OFFSET_MINUTES,
					"jummah_offset": OFFSET_MINUTES}