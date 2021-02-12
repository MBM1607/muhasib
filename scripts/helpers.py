'''File to store all the helper functions'''

import datetime
import math

from plyer import notification
from plyer.utils import platform
from pytz import timezone

# Earth's parameters as a sphere according to WGS-84
# https://en.wikipedia.org/wiki/World_Geodetic_System#WGS84
FLATTENING = 1/298.257223563
EQUATOR_RADIUS = 6378137.0
POLES_RADIUS = 6356752.314245


def is_float(s):
	'''Return if the passed string is a float or not'''
	try:
		float(s)
		return True
	except ValueError:
		return False

def notify(title="", message="", timeout=4, ticker="", mode="toast"):
	'''Send a notification'''
	kwargs = {"title": title, "message": message, "ticker": ticker, "timeout": timeout}

	if mode == "simple":
		kwargs["app_name"] = "Muhasib"
		if platform == "win":
			kwargs["app_icon"] = "data/logo.ico"
		else:
			kwargs["app_icon"] = "data/logo.png"
	elif mode == "toast":
		kwargs["toast"] = True
	try:
		notification.notify(**kwargs)
	except NotImplementedError:
		print("Error: System does not support notifications")

def vincenty_distance(lat1, lon1, lat2, lon2):
	'''Given two points calculate the distance between the two points using vincenty's formula'''

	# Convert all angles to radians
	lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))

	# Pre-calculate the trigonometric values so that the calculations are not repeated
	tanlat1 = (1 - FLATTENING) * math.tan(lat1)
	coslat1 = 1 / math.sqrt(1 + tanlat1**2)
	sinlat1 = tanlat1 * coslat1
	tanlat2 = (1 - FLATTENING) * math.tan(lat2)
	coslat2 = 1 / math.sqrt(1 + tanlat2**2)
	sinlat2 = tanlat2 * coslat2

	# Difference between longitudes
	original_lon = lon2 - lon1

	iteration_limit = 100
	lon = original_lon
	new_lon = original_lon + 1

	while abs(lon - new_lon) > 1e-12 and iteration_limit > 0:
		sinlon = math.sin(lon)
		coslon = math.cos(lon)
		angular_sep_sin = ((coslat2 * sinlon) ** 2) + ((coslat1 * sinlat2 - sinlat1 * coslat2 * coslon) ** 2)
		angular_sep_sin = math.sqrt(angular_sep_sin)
		if angular_sep_sin == 0:
			return 0 # co-incident points
		angular_sep_cos = sinlat1 * sinlat2 + coslat1 * coslat2 * coslon
		angular_sep = math.atan2(angular_sep_sin, angular_sep_cos)
		azimuth_sin = coslat1 * coslat2 * sinlon / angular_sep_sin
		cos_sqr_azimuth = 1 - (azimuth_sin ** 2)
		if cos_sqr_azimuth:
			cos_angular_mid_sep = angular_sep_cos - 2 * sinlat1 * sinlat2 / cos_sqr_azimuth
		else:
			cos_angular_mid_sep = 0 # equatorial line: cos_sqr_azimuth = 0
		C = FLATTENING / 16 * cos_sqr_azimuth * (4 + FLATTENING * (4 - 3 * cos_sqr_azimuth))
		new_lon = lon
		lon = original_lon + (1 - C) * FLATTENING * azimuth_sin * (angular_sep + C * angular_sep_sin * (cos_angular_mid_sep + C * angular_sep_cos * (-1 + 2 * (cos_angular_mid_sep) ** 2)))
		iteration_limit -= 1

	if not iteration_limit:
		raise ValueError("Formula failed to converge")

	u_sqr = cos_sqr_azimuth * ((EQUATOR_RADIUS ** 2) - (POLES_RADIUS ** 2)) / (POLES_RADIUS ** 2)
	A = 1 + u_sqr/16384 * (4096 + u_sqr * (-768 + u_sqr * (320 - 175 * u_sqr)))
	B = u_sqr / 1024 * (256 + u_sqr * (-128 + u_sqr * (74 - 47 * u_sqr)))
	delta_angular_sep = B * angular_sep_sin * (cos_angular_mid_sep + B / 4 * (angular_sep_cos * (-1 + 2 * (cos_angular_mid_sep ** 2)) \
				- B / 6 * cos_angular_mid_sep * (-3 + 4 * (angular_sep_sin ** 2)) * (-3 + 4 * (cos_angular_mid_sep ** 2))))

	return POLES_RADIUS * A * (angular_sep - delta_angular_sep)

def _check_type(s):
	'''Check if the given parameter is a string'''
	if not isinstance(s, str):
		raise TypeError(f"Expected str or unicode, got {type(s).__name__}")

def daterange(start_date, end_date):
	'''Create a range of dates from the start to the end date'''
	for n in range(int((end_date - start_date).days)):
		yield start_date + datetime.timedelta(n)

def is_even(num):
	'''Takes a number and return True if the number is even else return false'''
	if num % 2:
		return False
	return True

def utcoffset(tz):
	'''Take the timezone name and return its UTC offset'''
	now = datetime.datetime.now(tz=timezone(tz))
	utc_offset = (now.utcoffset().days * 24) + (now.utcoffset().seconds / 3600)
	return utc_offset

'''
Jellyfish jaro-winkler algorithm copyright

Copyright (c) 2015, James Turk
Copyright (c) 2015, Sunlight Foundation

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

	* Redistributions of source code must retain the above copyright notice,
	  this list of conditions and the following disclaimer.
	* Redistributions in binary form must reproduce the above copyright notice,
	  this list of conditions and the following disclaimer in the documentation
	  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

def jaro_winkler(s1, s2, long_tolerance=False):
	'''Return the string metric distance between the two provided strings using the jaro-winkler algorithm'''
	return _jaro_winkler(s1, s2, long_tolerance, True)

def _jaro_winkler(ying, yang, long_tolerance, winklerize):
	_check_type(ying)
	_check_type(yang)

	ying_len = len(ying)
	yang_len = len(yang)

	if not ying_len or not yang_len:
		return 0.0

	min_len = max(ying_len, yang_len)
	search_range = (min_len // 2) - 1
	if search_range < 0:
		search_range = 0

	ying_flags = [False]*ying_len
	yang_flags = [False]*yang_len

	# looking only within search range, count & flag matched pairs
	common_chars = 0
	for i, ying_ch in enumerate(ying):
		low = i - search_range if i > search_range else 0
		hi = i + search_range if i + search_range < yang_len else yang_len - 1
		for j in range(low, hi+1):
			if not yang_flags[j] and yang[j] == ying_ch:
				ying_flags[i] = yang_flags[j] = True
				common_chars += 1
				break

	# short circuit if no characters match
	if not common_chars:
		return 0.0

	# count transpositions
	k = trans_count = 0
	for i, ying_f in enumerate(ying_flags):
		if ying_f:
			for j in range(k, yang_len):
				if yang_flags[j]:
					k = j + 1
					break
			if ying[i] != yang[j]:
				trans_count += 1
	trans_count /= 2

	# adjust for similarities in nonmatched characters
	common_chars = float(common_chars)
	weight = ((common_chars/ying_len + common_chars/yang_len +
			  (common_chars-trans_count) / common_chars)) / 3

	# winkler modification: continue to boost if strings are similar
	if winklerize and weight > 0.7 and ying_len > 3 and yang_len > 3:
		# adjust for up to first 4 chars in common
		j = min(min_len, 4)
		i = 0
		while i < j and ying[i] == yang[i] and ying[i]:
			i += 1
		if i:
			weight += i * 0.1 * (1.0 - weight)

		# optionally adjust for long strings
		# after agreeing beginning chars, at least two or more must agree and
		# agreed characters must be > half of remaining characters
		if (long_tolerance and min_len > 4 and common_chars > i+1 and
				2 * common_chars >= min_len + i):
			weight += ((1.0 - weight) * (float(common_chars-i-1) / float(ying_len+yang_len-i*2+2)))

	return weight
