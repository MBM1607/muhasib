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