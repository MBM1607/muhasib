'''Module for the location's form and all related functionality'''

import threading

from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.properties import ObjectProperty
from plyer import gps
from plyer.utils import platform

import constants
from custom_widgets import (CustomModalView, CustomTextInput, LoadingPopup,
							TextButton)
from helpers import is_even, is_float, jaro_winkler, notify, vincenty_distance

try:
	from android.permissions import Permission, request_permissions
except ImportError:
	# Ignore the import if not on android
	pass

class LocationPopup(CustomModalView):
	'''Location Popup with various methods to determine current location'''

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.locations_data = {}
		for data in self.app.database.get_locations_data():
			# Case if region is not specified
			if not data[1]:
				location = ", ".join((data[0], data[2]))
				self.locations_data[location] = data
			else:
				location = ", ".join(data[:3])
				self.locations_data[location] = data

		self.loading_popup = LoadingPopup()

		self.bind(on_pre_open=lambda _: self.create_locations_data())
		self.bind(on_dismiss=lambda _: self.destroy_locations_data())

		if platform == "android":
			gps.configure(on_location=self.gps_location)
			self.located = False

	def request_gps_permission(self):
		'''Get the user's permission to access gps'''
		if platform == "android":
			request_permissions([Permission.ACCESS_FINE_LOCATION], callback=self.locate_with_gps)
		else:
			notify(title="GPS Needed", message="This device does not have a gps")

	def locate_with_gps(self, perm_names, perms):
		'''Select a location with gps'''
		if perms[0]:
			gps.start(1000, 1)
			self.timeout_event = Clock.schedule_once(lambda _: self.gps_timeout(), 60)
			self.loading_popup.open()
		else:
			notify(title="Location Permission", message="Permission is needed to get location")

	def gps_timeout(self):
		'''Cancel the gps location callback and send a toast notification informing the user'''
		gps.stop()
		notify(title="GPS Timeout", message="Check your internet connection")
		self.loading_popup.dismiss()

	@mainthread
	def gps_location(self, lat=0.0, lon=0.0, speed=0.0, bearing=0.0, altitude=0.0, accuracy=0.0):
		'''Gps on location callback to get location from latitude and longitude'''
		if not self.located:
			self.located = True
			gps.stop()
			self.timeout_event.cancel()
			thread = threading.Thread(target=self.get_location_from_coords, args=(lat, lon, altitude))
			thread.start()

	def change_location(self, location):
		'''Change the app's location to the location passed in'''
		self.app.change_location(location, *self.locations_data[location][3:])

	def create_locations_data(self):
		'''Create the location popups'''

		self.location_form = LocationForm(self)
		self.latlon_form = LatLonPopup(self)

	def destroy_locations_data(self):
		'''Remove the location popups'''
		self.location_form = None
		self.latlon_form = None
		self.loading_popup = None

	def open_location_form(self):
		'''Open the location form to select location with its name'''
		self.location_form.open()

	def open_latlon_popup(self):
		'''Open the latlong popup to select location with manual latitude, longitude'''
		self.latlon_form.open()

	def get_location_from_coords(self, lat, lon, alt=0.0):
		'''Get location from latitude and longitude'''
		distances = {}
		for location in self.locations_data.keys():
			location_lat = self.locations_data[location][3]
			location_lon = self.locations_data[location][4]
			try:
				distances[vincenty_distance(lat, lon, location_lat, location_lon)] = location
			except ValueError:
				pass

		entered_location = distances[min(distances)]
		if not alt:
			alt = self.locations_data[entered_location][5]

		self.app.change_location(entered_location, lat, lon, alt, *self.locations_data[entered_location][6:])
		self.loading_popup.dismiss()

	def give_location_suggestions(self, text):
		'''Use jaro-winkler algorithm to give location suggestions for the the input text'''
		suggestions = {}
		for location in self.locations_data.keys():
			score = jaro_winkler(location, text)
			if score > 0.7:
				suggestions[score] = location
		keys = sorted(suggestions.keys(), reverse=True)

		return {key: suggestions[key] for key in keys}


class LocationForm(CustomModalView):
	'''Class for location form to get user's location'''
	location_text = ObjectProperty()
	suggestions_list = ObjectProperty()

	def __init__(self, location_popup=None,**kwargs):
		super().__init__(**kwargs)
		self.location_popup = location_popup

	def check_input_location(self, _=None):
		'''Check if the input location is a valid location if not then open the suggestions'''

		if self.location_text.text in self.location_popup.locations_data.keys():
			self.change_location(self.location_text.text)
		elif self.location_text.text:
			self.location_popup.loading_popup.open()
			loading_thread = threading.Thread(target=self.add_suggestions)
			loading_thread.start()

	def add_suggestions(self):
		'''Populate the layout with suggestions'''
		text = self.location_text.text
		suggestions = self.location_popup.give_location_suggestions(text)
		self.suggestions_list.data = []
		for i, key in enumerate(suggestions.keys()):
			if is_even(i):
				bg_color = constants.MAIN_COLOR
			else:
				bg_color = constants.SECONDRY_COLOR

			self.suggestions_list.data.append({"text": suggestions[key], "background_color": bg_color,
												"func": self.change_location})

		self.location_popup.loading_popup.dismiss()

	def change_location(self, text):
		'''Change the location to the selected value and close the form'''
		self.location_popup.change_location(text)
		self.suggestions_list.data = []
		self.dismiss()


class LocationText(CustomTextInput):
	'''Text Input for the location form'''

	def on_text(self, instance, value):
		'''Make the text into a title'''
		self.text = value.title()


class LocationButton(TextButton):
	'''Button for the location suggestions'''
	func = ObjectProperty()

	def __init__(self, func=print, **kwargs):
		super().__init__(**kwargs)

		self.func = func
		self.bind(on_release=lambda _: self.func(self.text))



class LatLonPopup(CustomModalView):
	'''Popup for the manual insertion of latitude and longitude'''
	lat = ObjectProperty()
	lon = ObjectProperty()

	def __init__(self, location_popup=None, **kwargs):
		super().__init__(**kwargs)
		self.location_popup = location_popup

	def change_location(self):
		'''Change the location with the entered value of lattitude and longitude'''
		try:
			lat, lon = float(self.lat.text), float(self.lon.text)
			self.location_popup.loading_popup.open()
			thread = threading.Thread(target=self.get_location, args=(lat, lon))
			thread.start()
		except ValueError:
			title = "Invalid Data"
			if not self.lat.text and not self.lon.text:
				message = "No values are entered"
			elif not self.lat.text:
				message = "Latitude has no value"
			elif not self.lon.text:
				message = "Longitude has no value"
			else:
				message = "One or more values cannot be converted to decimals"
			notify(title=title,message=message)

	def get_location(self, lat, lon):
		'''Get the location from these latitude and longitude by calling popup's method'''
		self.location_popup.get_location_from_coords(lat, lon)
		self.dismiss()


class LatLonText(CustomTextInput):
	'''Text input for the latitude and longitude'''

	def insert_text(self, substring, from_undo=False):
		'''Overwrite the insert_text method of TextInput to only accept floats'''
		allowed = (".", "-")
		if substring.isdecimal() or any(substring == x and x not in self.text for x in allowed):
			return super().insert_text(substring, from_undo=from_undo)

	def on_text(self, instance, value):
		'''When text value is changed check if its valid value and color it accordingly'''
		if is_float(value):
			self.foreground_color = constants.MAIN_COLOR
			self.selection_color = (*constants.MAIN_COLOR[:3], 0.5)
		else:
			self.foreground_color = constants.WARNING_COLOR
			self.selection_color = (*constants.WARNING_COLOR[:3], 0.5)
