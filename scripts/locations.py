'''Module for the location's form and all related functionality'''

import json
import threading

from kivy.app import App
from kivy.properties import DictProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView

import constants
from custom_widgets import CustomModalView, LoadingPopup, TextButton
from helpers import is_even, jaro_winkler


class LocationDropDown(DropDown):
	'''Dropdown for the location suggestions'''

	def dismiss(self):
		'''Clear children when dismissed'''
		self.clear_widgets()
		super().dismiss()


class LocationButton(TextButton):
	pass


class LocationForm(CustomModalView):
	'''Class for location form to get user's location'''
	location_text = ObjectProperty()
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.locations_data = {}
		self.locations = set()
		self.bind(on_pre_open=lambda _: self.create_locations_data())
		self.bind(on_dismiss=lambda _: self.destroy_locations_data())

	def create_locations_data(self):
		'''Load the cities data and extract the relevent information from it'''
		with open("data/cities.json") as locations_data:
			for data in json.load(locations_data):
				# Case if region is not specified
				if not data[2]:
					location = ", ".join((data[0], data[1]))
					self.locations_data[location] = data
					self.locations.add(location)
				else:
					location = ", ".join((data[0], data[2], data[1]))
					self.locations_data[location] = data
					self.locations.add(location)
		
		# Create the locations dropdown
		self.suggestion_dropdown = LocationDropDown()
		self.loading_popup = LoadingPopup()
		self.suggestion_dropdown.bind(on_select=self.change_location)

	def destroy_locations_data(self):
		'''Remove all location data from the class'''
		self.location_text.text = ""
		self.location_data = {}
		self.locations = set()
		self.suggestion_dropdown = None
		self.loading_popup = None

	def check_input_location(self, _=None):
		'''Check if the input location is a valid location if not then open the suggestions'''
		text = self.location_text.text.title()
		self.location_text.text = self.location_text.text.title()

		# Change the location to input text if it is a valid location
		if text in self.locations:
			self.change_location(self, text)
		elif text:
			self.loading_popup.open()
			loading_thread = threading.Thread(target=self.suggestion_dropdown_open, args=(text,))
			loading_thread.start()

	def suggestion_dropdown_open(self, text):
		'''Open and populate the location dropdown with suggestions'''
		suggestions = self.give_location_suggestions(text)
		for i, key in enumerate(suggestions.keys()):
			if is_even(i):
				bg_color = constants.MAIN_COLOR
			else:
				bg_color = constants.SECONDRY_COLOR

			btn = LocationButton(text=suggestions[key], background_color=bg_color)
			btn.bind(on_release=lambda btn: self.suggestion_dropdown.select(btn.text))
			self.suggestion_dropdown.add_widget(btn)
		if text == self.location_text.text:
			self.suggestion_dropdown.open(self.location_text)

		self.loading_popup.dismiss()

	def give_location_suggestions(self, text):
		'''Use jaro-winkler algorithm to give location suggestions for the the input text'''
		suggestions = {}
		for location in self.locations:
			score = jaro_winkler(location, text)
			if score > 0.7:
				suggestions[score] = location
		keys = sorted(suggestions.keys(), reverse=True)

		return {key: suggestions[key] for key in keys}

	def change_location(self, instance, value):
		'''Change the location to the selected value and close the form'''

		self.app.change_location(value, *self.locations_data[value][3:])
		self.dismiss()
