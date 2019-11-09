'''
--------------------- Copyright Block ----------------------

praytimes.py: Prayer Times Calculator (ver 2.3)
Copyright (C) 2007-2011 PrayTimes.org

Original js Code: Hamid Zarrabi-Zadeh

License: GNU LGPL v3.0

TERMS OF USE:
	Permission is granted to use this code, with or
	without modification, in any website or application
	provided that credit is given to the original work
	with a link back to PrayTimes.org.

This program is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY.

PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK.


--------------------- Help and Manual ----------------------

User's Manual:
http://praytimes.org/manual

Calculation Formulas:
http://praytimes.org/calculation

'''

import math


class PrayerTimes():
	''' A class to hold all the prayer times calculation capabilities '''

	def __init__(self) :
		
		self.time_suffixes = ["am", "pm"]
		self.timezone = 0
		self.time_format = "24h"
		self.asr_param = "Standard"
		self.show_imsak_time = True
		self.is_jummah = False

		self.lat = 0
		self.lng = 0
		self.alt = 0

		self.time_names = {'imsak', 'fajr', 'sunrise', 'dhuhr', 'asr',
							'sunset', 'maghrib', 'isha', 'midnight'}

		# Optional offsets to times
		self.offset = {x : 0 for x in self.time_names}


		# Default Parameters in Calculation Methods
		default_params = {
			'maghrib': '0 min', 'midnight': 'Standard'
		}
		

		# Calculation Methods
		self.methods = {
			'Muslim World League':
				{**{'fajr': 18, 'isha': 17}, **default_params},
			'Islamic Society of North America (ISNA)':
				{**{'fajr': 15, 'isha': 15}, **default_params},
			'Egyptian General Authority of Survey':
				{**{'fajr': 19.5, 'isha': 17.5}, **default_params},
			'Umm Al-Qura University, Makkah':
				{**{'fajr': 18.5, 'isha': '90 min'}, **default_params},  # fajr was 19 degrees before 1430 hijri
			'University of Islamic Sciences, Karachi':
				{**{'fajr': 18, 'isha': 18}, **default_params},
			'Gulf Region':
				{**{'fajr': 19.5, 'isha': '90 min'}, **default_params},
			'Kuwait':
				{**{'fajr': 18, 'isha': 17.5}, **default_params},
			'Qatar':
				{**{'fajr': 18, 'isha': '90 min'}, **default_params},
			'Majlis Ugama Islam Singapura, Singapore':
				{**{'fajr': 20, 'isha': 18}, **default_params},
			'Union Organization Islamic de France':
				{**{'fajr': 12, 'isha': 12}, **default_params},
			'Diyanet İşleri Başkanlığı, Turkey':
				{**{'fajr': 18, 'isha': 17}, **default_params},
			'Spiritual Administration of Muslims of Russia':
				{**{'fajr': 16, 'isha': 15}, **default_params},
			'Institute of Geophysics, University of Tehran':
				{'fajr': 17.7, 'isha': 14, 'maghrib': 4.5, 'midnight': 'Jafari'},  # isha is not explicitly specified in this method
			'Shia Ithna-Ashari, Leva Institute, Qum':
				{'fajr': 16, 'isha': 14, 'maghrib': 4, 'midnight': 'Jafari'}
		}


		# initialize settings
		self.settings = {
			"imsak": '10 min',
			"dhuhr": '0 min',
			"jummah": '0 min',
			"high_lats": 'Night Middle',
		}
		self.set_method("Muslim World League")


	def set_method(self, method):
		''' Set the method of measuring prayer time '''
		self.settings.update(self.methods[method])

	def get_times(self, date):
		''' Return prayer times for a given date '''
		if date.weekday() == 4:
			self.is_jummah = True

		self.jDate = self.julian(date.year, date.month, date.day) - self.lng / (15 * 24.0)
		times = self.compute_times()

		if not self.show_imsak_time:
			del times["imsak"]
		return times

	def get_formatted_time(self, time, suffixes = None):
		''' Convert float time to the given format (see time_formats) '''
		if math.isnan(time):
			return '----'
		if suffixes == None:
			suffixes = self.time_suffixes

		time = self.fixhour(time+ 0.5/ 60)  # add 0.5 minutes to round
		hours = math.floor(time)

		minutes = math.floor((time- hours)* 60)
		suffix = suffixes[ 0 if hours < 12 else 1 ] if self.time_format == '12h' else ''
		formattedTime = f"%02d:%02d" % (hours, minutes) if self.time_format == "24h" else "%d:%02d" % ((hours+11)%12+1, minutes)
		return formattedTime + " " + suffix


	#---------------------- Calculation Functions -----------------------

	def mid_day(self, time):
		''' Compute mid-day time '''
		eqt = self.sun_position(self.jDate + time)[1]
		return self.fixhour(12 - eqt)

	def sun_angle_time(self, angle, time, direction = None):
		''' Compute the time at which sun reaches a specific angle below horizon '''

		try:
			decl = self.sun_position(self.jDate + time)[0]
			noon = self.mid_day(time)
			t = 1/15.0* self.arccos((-self.sin(angle)- self.sin(decl)* self.sin(self.lat))/
					(self.cos(decl)* self.cos(self.lat)))
			return noon+ (-t if direction == 'ccw' else t)
		except ValueError:
			return float('nan')

	def asr_time(self, factor, time):
		''' Compute asr time '''
		decl = self.sun_position(self.jDate + time)[0]
		angle = -self.arccot(factor + self.tan(abs(self.lat - decl)))
		return self.sun_angle_time(angle, time)

	def sun_position(self, jd):
		''' Compute declination angle of sun and equation of time
	  		Ref: http://aa.usno.navy.mil/faq/docs/SunApprox.php '''

		D = jd - 2451545.0
		g = self.fixangle(357.529 + 0.98560028* D)
		q = self.fixangle(280.459 + 0.98564736* D)
		L = self.fixangle(q + 1.915* self.sin(g) + 0.020* self.sin(2*g))

		#R = 1.00014 - 0.01671*self.cos(g) - 0.00014*self.cos(2*g)
		e = 23.439 - 0.00000036* D

		RA = self.arctan2(self.cos(e)* self.sin(L), self.cos(L))/ 15.0
		eqt = q/15.0 - self.fixhour(RA)
		decl = self.arcsin(self.sin(e)* self.sin(L))

		return (decl, eqt)

	def julian(self, year, month, day):
		''' Convert Gregorian date to Julian day
			Ref: Astronomical Algorithms by Jean Meeus '''

		if month <= 2:
			year -= 1
			month += 12
		a = math.floor(year / 100)
		b = 2 - a + math.floor(a / 4)
		return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5



	#---------------------- Compute Prayer Times -----------------------

	def compute_prayer_times(self, times):
		''' Compute prayer times at given julian date '''
		times = self.day_portion(times)
		params = self.settings

		imsak   = self.sun_angle_time(self.eval(params['imsak']), times['imsak'], 'ccw')
		fajr    = self.sun_angle_time(self.eval(params['fajr']), times['fajr'], 'ccw')
		sunrise = self.sun_angle_time(self.rise_set_angle(self.alt), times['sunrise'], 'ccw')
		dhuhr   = self.mid_day(times['dhuhr'])
		asr     = self.asr_time(self.asr_factor(), times['asr'])
		sunset  = self.sun_angle_time(self.rise_set_angle(self.alt), times['sunset'])
		maghrib = self.sun_angle_time(self.eval(params['maghrib']), times['maghrib'])
		isha    = self.sun_angle_time(self.eval(params['isha']), times['isha'])
		return {
			'imsak': imsak, 'fajr': fajr, 'sunrise': sunrise, 'dhuhr': dhuhr,
			'asr': asr, 'sunset': sunset, 'maghrib': maghrib, 'isha': isha
		}

	def compute_times(self):
		''' Compute prayer times '''
		num_iterations = 1
		times = {
			'imsak': 5, 'fajr': 5, 'sunrise': 6, 'dhuhr': 12,
			'asr': 13, 'sunset': 18, 'maghrib': 18, 'isha': 18
		}

		# main iterations
		for _ in range(num_iterations):
			times = self.compute_prayer_times(times)

		
		times = self.adjust_times(times)
		# add midnight time
		if self.settings['midnight'] == 'Jafari':
			times['midnight'] = times['sunset'] + self.time_diff(times['sunset'], times['fajr']) / 2
		else:
			times['midnight'] = times['sunset'] + self.time_diff(times['sunset'], times['sunrise']) / 2

		times = self.tune_times(times)
		return self.modify_formats(times)

	def adjust_times(self, times):
		''' Adjust times in a prayer time array '''
		tz_adjust = self.timezone - self.lng / 15.0
		for t in times.keys():
			times[t] += tz_adjust

		if self.settings['high_lats'] != 'None':
			times = self.adjust_high_lats(times)

		if self.is_min(self.settings['imsak']):
			times['imsak'] = times['fajr'] - self.eval(self.settings['imsak']) / 60.0
		# need to ask about 'min' settings
		if self.is_min(self.settings['maghrib']):
			times['maghrib'] = times['sunset'] - self.eval(self.settings['maghrib']) / 60.0

		if self.is_min(self.settings['isha']):
			times['isha'] = times['maghrib'] - self.eval(self.settings['isha']) / 60.0
		times['dhuhr'] += self.eval(self.settings['dhuhr']) / 60.0

		if self.is_jummah:
			times["dhuhr"] += self.eval(self.settings["jummah"]) / 60.0

		return times

	def asr_factor(self):
		''' Get asr shadow factor '''
		methods = {'Standard': 1, 'Hanafi': 2}
		return methods[self.asr_param] if self.asr_param in methods else self.eval(self.asr_param)

	def rise_set_angle(self, elevation = 0):
		''' Return sun angle for sunset/sunrise '''
		elevation = 0 if elevation == None else elevation
		return 0.833 + 0.0347 * math.sqrt(elevation) # an approximation

	def tune_times(self, times):
		''' Apply offsets to the times '''
		for name in times.keys():
			times[name] += self.offset[name] / 60.0
		return times

	def modify_formats(self, times):
		''' Convert times to given time format '''
		for name in times.keys():
			times[name] = self.get_formatted_time(times[name])
		return times

	def adjust_high_lats(self, times):
		''' Adjust times for locations in higher latitudes '''

		params = self.settings
		nightTime = self.time_diff(times['sunset'], times['sunrise']) # sunset to sunrise
		times['imsak'] = self.adjust_HL_time(times['imsak'], times['sunrise'], self.eval(params['imsak']), nightTime, 'ccw')
		times['fajr']  = self.adjust_HL_time(times['fajr'], times['sunrise'], self.eval(params['fajr']), nightTime, 'ccw')
		times['isha']  = self.adjust_HL_time(times['isha'], times['sunset'], self.eval(params['isha']), nightTime)
		times['maghrib'] = self.adjust_HL_time(times['maghrib'], times['sunset'], self.eval(params['maghrib']), nightTime)
		return times

	def adjust_HL_time(self, time, base, angle, night, direction = None):
		''' Adjust a time for higher latitudes '''

		portion = self.night_portion(angle, night)
		diff = self.time_diff(time, base) if direction == 'ccw' else self.time_diff(base, time)
		if math.isnan(time) or diff > portion:
			time = base + (-portion if direction == 'ccw' else portion)
		return time

	def night_portion(self, angle, night):
		''' The night portion used for adjusting times in higher latitudes '''

		method = self.settings['high_lats']
		portion = 1/2.0  # midnight
		if method == 'Angle Based':
			portion = 1/60.0 * angle
		if method == 'One Seventh':
			portion = 1/7.0
		return portion * night

	def day_portion(self, times):
		''' Convert hours to day portions '''
		for i in times:
			times[i] /= 24.0
		return times


	#---------------------- Misc Functions -----------------------

	def time_diff(self, time1, time2):
		''' Compute the difference between two times '''
		return self.fixhour(time2- time1)

	def eval(self, st):
		''' Convert given string into a number '''
		if isinstance(st, str):
			return float(st.split()[0])
		return st

	def is_min(self, arg):
		''' Detect if input contains 'min' '''
		return isinstance(arg, str) and arg.find('min') > -1

	def get_qibla(self):
		''' Get the qibla direction from current position '''
		qaba_lat = 21.423333
		qaba_lng = 39.823333

		numerator = self.sin(qaba_lng - self.lng)
		denominator = (self.cos(self.lat) * self.tan(qaba_lat)) - (self.sin(self.lat) * self.cos(qaba_lng - self.lng))

		return round(self.arctan2(numerator, denominator))


	#----------------- Degree-Based Math Functions -------------------

	def sin(self, d): return math.sin(math.radians(d))
	def cos(self, d): return math.cos(math.radians(d))
	def tan(self, d): return math.tan(math.radians(d))

	def arcsin(self, x): return math.degrees(math.asin(x))
	def arccos(self, x): return math.degrees(math.acos(x))
	def arctan(self, x): return math.degrees(math.atan(x))

	def arccot(self, x): return math.degrees(math.atan(1.0/x))
	def arctan2(self, y, x): return math.degrees(math.atan2(y, x))

	def fixangle(self, angle): return self.fix(angle, 360.0)
	def fixhour(self, hour): return self.fix(hour, 24.0)

	def fix(self, a, mode):
		if math.isnan(a):
			return a
		a = a - mode * (math.floor(a / mode))
		return a + mode if a < 0 else a
