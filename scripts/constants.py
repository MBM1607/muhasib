''' Module for all the global constants of the app '''

MAIN_COLOR = (0, 64/255, 52/255, 1)
SECONDRY_COLOR = (16/255, 112/255, 94/255, 1)
TERNARY_COLOR = (20/255, 184/255, 154/255, 1)
CAUTION_COLOR = (230/255, 179/255, 50/255, 1)
WARNING_COLOR = (192/255, 43/255, 38/255, 1)
GREY_COLOR = (240/255, 240/255, 240/255, 1)

PRAYER_CATEGORY_NAMES = ('Group', 'Alone', 'Delayed', 'Not Prayed')
PRAYER_CATEGORY_COLORS = {'Group': SECONDRY_COLOR, 'Alone': TERNARY_COLOR,
						'Delayed': CAUTION_COLOR, 'Not Prayed': WARNING_COLOR}
PRAYER_NAMES = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")