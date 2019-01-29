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

	def __init__(self, method = "MWL", time_format="24h") :
		
		self.time_format = time_format
		self.time_suffixes = ["am", "pm"]
		self.invalid_time =  '-----'
		self.num_iterations = 1

		self.time_names = {'imsak', 'fajr', 'sunrise', 'dhuhr', 'asr',
							'sunset', 'maghrib', 'isha', 'midnight'}

		self.offset = {x : 0 for x in self.time_names}


		# Default Parameters in Calculation Methods
		self.default_params = {
			'maghrib': '0 min', 'midnight': 'Standard'
		}
		

		# Calculation Methods
		self.methods = {
			'MWL': {
				'name': 'Muslim World League',
				'params': {**{'fajr': 18, 'isha': 17}, **self.default_params}},
			'ISNA': {
				'name': 'Islamic Society of North America (ISNA)',
				'params': {**{'fajr': 15, 'isha': 15}, **self.default_params}},
			'Egypt': {
				'name': 'Egyptian General Authority of Survey',
				'params': {**{'fajr': 19.5, 'isha': 17.5}, **self.default_params}},
			'Makkah': {
				'name': 'Umm Al-Qura University, Makkah',
				'params': {**{'fajr': 18.5, 'isha': '90 min'}, **self.default_params}},  # fajr was 19 degrees before 1430 hijri
			'Karachi': {
				'name': 'University of Islamic Sciences, Karachi',
				'params': {**{'fajr': 18, 'isha': 18}, **self.default_params}},
			'Tehran': {
				'name': 'Institute of Geophysics, University of Tehran',
				'params': {'fajr': 17.7, 'isha': 14, 'maghrib': 4.5, 'midnight': 'Jafari'}},  # isha is not explicitly specified in this method
			'Jafari': {
				'name': 'Shia Ithna-Ashari, Leva Institute, Qum',
				'params': {'fajr': 16, 'isha': 14, 'maghrib': 4, 'midnight': 'Jafari'}}
		}

		
		# initialize settings
		self.settings = {
			"imsak"    : '10 min',
			"dhuhr"    : '0 min',
			"asr"      : 'Standard',
			"highLats" : 'NightMiddle'
		}
		self.set_method(method)


	# Set the method of measuring prayer time
	def set_method(self, method):
		self.settings.update(self.methods[method]["params"])
		self.calc_method = method

	# return prayer times for a given date
	def get_times(self, date, coords, timezone, dst = 0):
		self.lat = coords[0]
		self.lng = coords[1]
		self.elv = coords[2] if len(coords) > 2 else 0
		if type(date).__name__ == 'date':
			date = (date.year, date.month, date.day)
		self.timeZone = timezone + (1 if dst else 0)
		self.jDate = self.julian(date[0], date[1], date[2]) - self.lng / (15 * 24.0)
		return self.compute_times()

	# convert float time to the given format (see time_formats)
	def get_formatted_time(self, time, format, suffixes = None):
		if math.isnan(time):
			return self.invalid_time
		if format == 'Float':
			return time
		if suffixes == None:
			suffixes = self.time_suffixes

		time = self.fixhour(time+ 0.5/ 60)  # add 0.5 minutes to round
		hours = math.floor(time)

		minutes = math.floor((time- hours)* 60)
		suffix = suffixes[ 0 if hours < 12 else 1 ] if format == '12h' else ''
		formattedTime = "%02d:%02d" % (hours, minutes) if format == "24h" else "%d:%02d" % ((hours+11)%12+1, minutes)
		return formattedTime + " " + suffix


	#---------------------- Calculation Functions -----------------------

	# compute mid-day time
	def mid_day(self, time):
		eqt = self.sun_position(self.jDate + time)[1]
		return self.fixhour(12 - eqt)

	# compute the time at which sun reaches a specific angle below horizon
	def sun_angle_time(self, angle, time, direction = None):
		try:
			decl = self.sun_position(self.jDate + time)[0]
			noon = self.mid_day(time)
			t = 1/15.0* self.arccos((-self.sin(angle)- self.sin(decl)* self.sin(self.lat))/
					(self.cos(decl)* self.cos(self.lat)))
			return noon+ (-t if direction == 'ccw' else t)
		except ValueError:
			return float('nan')

	# compute asr time
	def asr_time(self, factor, time):
		decl = self.sun_position(self.jDate + time)[0]
		angle = -self.arccot(factor + self.tan(abs(self.lat - decl)))
		return self.sun_angle_time(angle, time)

	# compute declination angle of sun and equation of time
	# Ref: http://aa.usno.navy.mil/faq/docs/SunApprox.php
	def sun_position(self, jd):
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

	# convert Gregorian date to Julian day
	# Ref: Astronomical Algorithms by Jean Meeus
	def julian(self, year, month, day):
		if month <= 2:
			year -= 1
			month += 12
		a = math.floor(year / 100)
		b = 2 - a + math.floor(a / 4)
		return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5



	#---------------------- Compute Prayer Times -----------------------

	# compute prayer times at given julian date
	def compute_prayer_times(self, times):
		times = self.day_portion(times)
		params = self.settings

		imsak   = self.sun_angle_time(self.eval(params['imsak']), times['imsak'], 'ccw')
		fajr    = self.sun_angle_time(self.eval(params['fajr']), times['fajr'], 'ccw')
		sunrise = self.sun_angle_time(self.rise_set_angle(self.elv), times['sunrise'], 'ccw')
		dhuhr   = self.mid_day(times['dhuhr'])
		asr     = self.asr_time(self.asr_factor(params['asr']), times['asr'])
		sunset  = self.sun_angle_time(self.rise_set_angle(self.elv), times['sunset'])
		maghrib = self.sun_angle_time(self.eval(params['maghrib']), times['maghrib'])
		isha    = self.sun_angle_time(self.eval(params['isha']), times['isha'])
		return {
			'imsak': imsak, 'fajr': fajr, 'sunrise': sunrise, 'dhuhr': dhuhr,
			'asr': asr, 'sunset': sunset, 'maghrib': maghrib, 'isha': isha
		}

	# compute prayer times
	def compute_times(self):
		times = {
			'imsak': 5, 'fajr': 5, 'sunrise': 6, 'dhuhr': 12,
			'asr': 13, 'sunset': 18, 'maghrib': 18, 'isha': 18
		}

		# main iterations
		for _ in range(self.num_iterations):
			times = self.compute_prayer_times(times)

		
		times = self.adjust_times(times)
		# add midnight time
		if self.settings['midnight'] == 'Jafari':
			times['midnight'] = times['sunset'] + self.time_diff(times['sunset'], times['fajr']) / 2
		else:
			times['midnight'] = times['sunset'] + self.time_diff(times['sunset'], times['sunrise']) / 2

		times = self.tune_times(times)
		return self.modify_formats(times)

	# adjust times in a prayer time array
	def adjust_times(self, times):
		params = self.settings
		tzAdjust = self.timeZone - self.lng / 15.0
		for t in times.keys():
			times[t] += tzAdjust

		if params['highLats'] != 'None':
			times = self.adjust_high_lats(times)

		if self.is_min(params['imsak']):
			times['imsak'] = times['fajr'] - self.eval(params['imsak']) / 60.0
		# need to ask about 'min' settings
		if self.is_min(params['maghrib']):
			times['maghrib'] = times['sunset'] - self.eval(params['maghrib']) / 60.0

		if self.is_min(params['isha']):
			times['isha'] = times['maghrib'] - self.eval(params['isha']) / 60.0
		times['dhuhr'] += self.eval(params['dhuhr']) / 60.0

		return times

	# get asr shadow factor
	def asr_factor(self, asrParam):
		methods = {'Standard': 1, 'Hanafi': 2}
		return methods[asrParam] if asrParam in methods else self.eval(asrParam)

	# return sun angle for sunset/sunrise
	def rise_set_angle(self, elevation = 0):
		elevation = 0 if elevation == None else elevation
		return 0.833 + 0.0347 * math.sqrt(elevation) # an approximation

	# apply offsets to the times
	def tune_times(self, times):
		for name in times.keys():
			times[name] += self.offset[name] / 60.0
		return times

	# convert times to given time format
	def modify_formats(self, times):
		for name in times.keys():
			times[name] = self.get_formatted_time(times[name], self.time_format)
		return times

	# adjust times for locations in higher latitudes
	def adjust_high_lats(self, times):
		params = self.settings
		nightTime = self.time_diff(times['sunset'], times['sunrise']) # sunset to sunrise
		times['imsak'] = self.adjust_HL_time(times['imsak'], times['sunrise'], self.eval(params['imsak']), nightTime, 'ccw')
		times['fajr']  = self.adjust_HL_time(times['fajr'], times['sunrise'], self.eval(params['fajr']), nightTime, 'ccw')
		times['isha']  = self.adjust_HL_time(times['isha'], times['sunset'], self.eval(params['isha']), nightTime)
		times['maghrib'] = self.adjust_HL_time(times['maghrib'], times['sunset'], self.eval(params['maghrib']), nightTime)
		return times

	# adjust a time for higher latitudes
	def adjust_HL_time(self, time, base, angle, night, direction = None):
		portion = self.night_portion(angle, night)
		diff = self.time_diff(time, base) if direction == 'ccw' else self.time_diff(base, time)
		if math.isnan(time) or diff > portion:
			time = base + (-portion if direction == 'ccw' else portion)
		return time

	# the night portion used for adjusting times in higher latitudes
	def night_portion(self, angle, night):
		method = self.settings['highLats']
		portion = 1/2.0  # midnight
		if method == 'AngleBased':
			portion = 1/60.0 * angle
		if method == 'OneSeventh':
			portion = 1/7.0
		return portion * night

	# convert hours to day portions
	def day_portion(self, times):
		for i in times:
			times[i] /= 24.0
		return times


	#---------------------- Misc Functions -----------------------

	# compute the difference between two times
	def time_diff(self, time1, time2):
		return self.fixhour(time2- time1)

	# convert given string into a number
	def eval(self, st):
		if isinstance(st, str):
			return float(st.split()[0])
		return st

	# detect if input contains 'min'
	def is_min(self, arg):
		return isinstance(arg, str) and arg.find('min') > -1


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
	
if __name__ == "__main__":
	from datetime import date
	print('Prayer Times for today in Waterloo/Canada\n'+ ('='* 41))
	times = PrayerTimes().get_times(date.today(), (43, -80), -5)
	for i in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha', 'Midnight']:
		print(i+ ': '+ times[i.lower()])
