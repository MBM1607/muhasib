'''Module for the location's form and all related functionality'''

import json
import threading

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.dropdown import DropDown

import constants
from custom_widgets import (CustomModalView, CustomTextInput, LoadingPopup,
							TextButton)
from helpers import is_even, is_float, jaro_winkler, notify, vincenty_distance


class LocationPopup(CustomModalView):
	'''Location Popup with various methods to determine current location'''

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.locations_data = {}

		self.bind(on_pre_open=lambda _: self.create_locations_data())
		self.bind(on_dismiss=lambda _: self.destroy_locations_data())

	def change_location(self, location):
		'''Change the app's location to the location passed in'''
		self.app.change_location(location, *self.locations_data[location][3:])

	def create_locations_data(self):
		'''Load the cities data and make locations datasets from it'''
		with open("data/cities.json") as locations_data:
			for data in json.load(locations_data):
				# Case if region is not specified
				if not data[2]:
					location = ", ".join((data[0], data[1]))
					self.locations_data[location] = data
				else:
					location = ", ".join((data[0], data[2], data[1]))
					self.locations_data[location] = data

		self.location_form = LocationForm(self)
		self.latlon_form = LatLonPopup(self)
		self.loading_popup = LoadingPopup()

	def destroy_locations_data(self):
		'''Get rid of all the locations datasets in the memory'''
		self.location_form = None
		self.latlon_form = None
		self.loading_popup = None
		self.locations_data = {}
		self.locations = set()

	def open_location_form(self):
		'''Open the location form to select location with its name'''
		self.location_form.open()

	def open_latlon_popup(self):
		'''Open the latlong popup to select location with manual latitude, longitude'''
		self.latlon_form.open()

	def locate_with_gps(self):
		'''Select a location with gps'''
		pass

	def get_location_from_latlon(self, lat, lon):
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
		self.app.change_location(entered_location, lat, lon, *self.locations_data[entered_location][5:])
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

	def __init__(self, location_popup=None,**kwargs):
		super().__init__(**kwargs)
		self.location_popup = location_popup

		self.suggestion_dropdown = LocationDropDown()
		self.suggestion_dropdown.bind(on_select=self.change_location)

	def check_input_location(self, _=None):
		'''Check if the input location is a valid location if not then open the suggestions'''

		if self.location_text.text in self.location_popup.locations_data.keys():
			self.change_location(self, self.location_text.text)
		elif self.location_text.text:
			self.location_popup.loading_popup.open()
			loading_thread = threading.Thread(target=self.suggestion_dropdown_open)
			loading_thread.start()

	def suggestion_dropdown_open(self):
		'''Open and populate the location dropdown with suggestions'''
		text = self.location_text.text
		suggestions = self.location_popup.give_location_suggestions(text)
		for i, key in enumerate(suggestions.keys()):
			if is_even(i):
				bg_color = constants.MAIN_COLOR
			else:
				bg_color = constants.SECONDRY_COLOR

			btn = LocationButton(text=suggestions[key], background_color=bg_color)
			btn.bind(on_release=lambda btn: self.suggestion_dropdown.select(btn.text))
			self.suggestion_dropdown.add_widget(btn)

		self.suggestion_dropdown.open(self.location_text)
		self.location_popup.loading_popup.dismiss()

	def change_location(self, instance, value):
		'''Change the location to the selected value and close the form'''
		self.location_popup.change_location(value)
		self.dismiss()


class LocationText(CustomTextInput):
	'''Text Input for the location form'''

	def on_text(self, instance, value):
		'''Make the text into a title'''
		self.text = value.title()


class LocationDropDown(DropDown):
	'''Dropdown for the location suggestions'''

	def dismiss(self):
		'''Clear children when dismissed'''
		self.clear_widgets()
		super().dismiss()


class LocationButton(TextButton):
	pass


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
			notify(title=title,message=message, mode="toast")

	def get_location(self, lat, lon):
		'''Get the location from these latitude and longitude by calling popup's method'''
		self.location_popup.get_location_from_latlon(lat, lon)
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
