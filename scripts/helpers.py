'''  File to store all the helper functions '''

import datetime

import pytz


def _check_type(s):
	''' Check if the given parameter is a string '''
	if not isinstance(s, str):
		raise TypeError(f"Expected str or unicode, got {type(s).__name__}")

def is_even(num):
	''' Takes a number and return True if the number is even else return false '''
	if num % 2:
		return False
	return True

def utcoffset(tz):
	''' Take the timezone name and return its UTC offset '''
	now = datetime.datetime.now(tz=pytz.timezone(tz))
	utc_offset = (now.utcoffset().days * 24) + (now.utcoffset().seconds / 3600)
	return utc_offset

def get_previous_monday(date):
	''' Take a date and return the previous monday from that date '''
	return date - datetime.timedelta(days=date.weekday())

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
	''' Return the string metric distance between the two provided strings using the jaro-winkler algorithm '''
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
