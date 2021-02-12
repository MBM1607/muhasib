# This file is part of convertdate.
# http://github.com/fitnr/convertdate

# Licensed under the MIT license:
# http://opensource.org/licenses/MIT
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

from math import trunc

import gregorian
from utils import ceil, jwday, monthcalendarhelper

EPOCH = 1948439.5

HAS_29_DAYS = (2, 4, 6, 8, 10)
HAS_30_DAYS = (1, 3, 5, 7, 9, 11)


def leap(year):
	'''Is a given year a leap year in the Islamic calendar'''
	return (((year * 11) + 14) % 30) < 11


def to_jd(year, month, day, adj=0):
	'''Determine Julian day count from Islamic date'''
	return (day + ceil(29.5 * (month - 1)) + (year - 1) * 354 + trunc((3 + (11 * year)) / 30) + EPOCH) - 1 + adj


def from_jd(jd, adj=0):
	'''Calculate Islamic date from Julian day'''

	jd = trunc(jd) + 0.5
	year = trunc(((30 * (jd - EPOCH)) + 10646) / 10631)
	month = min(12, ceil((jd - (29 + to_jd(year, 1, 1, adj=adj))) / 29.5) + 1)
	day = int(jd - to_jd(year, month, 1, adj=adj)) + 1
	return (year, month, day)


def from_gregorian(year, month, day, adj=0):
	return from_jd(gregorian.to_jd(year, month, day), adj=adj)


def to_gregorian(year, month, day, adj=0):
	return gregorian.from_jd(to_jd(year, month, day, adj=adj))


def month_length(year, month):
	if month in HAS_30_DAYS or (month == 12 and leap(year)):
		return 30

	return 29


def monthcalendar(year, month, adj=0):
	start_weekday = jwday(to_jd(year, month, 1, adj=adj))
	monthlen = month_length(year, month)
	return monthcalendarhelper(start_weekday, monthlen)
