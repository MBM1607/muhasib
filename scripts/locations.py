''' Module for the location's form and all related functionality '''

import json

from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty

from custom_widgets import CustomButton, CustomModalView
from helpers import jaro_winkler, is_even
import constants

class LocationDropDown(DropDown):
	''' Dropdown for the location suggestions '''

	def dismiss(self):
		''' Clear children when dismissed '''
		self.clear_widgets()
		super().dismiss()


class LocationButton(CustomButton):
	pass


class LocationForm(CustomModalView):
	''' Class for location form to get user's location '''
	location_text = ObjectProperty()
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.locations_data = {}
		self.locations = set()

	def on_pre_open(self):
		''' Load the data required for function of the popup '''

		# Extract the city, region and country from the data and make a locations set and a dictionary with it
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

		self.suggestion_dropdown = LocationDropDown()
		self.suggestion_dropdown.bind(on_select=self.change_location)

	def on_pre_dismiss(self):
		''' Remove the data from the class'''
		self.location_text.text = ""
		self.locations_data = {}
		self.locations = set()
		self.suggestion_dropdown = None

	def check_input_location(self, _=None):
		''' Check if the input location is a valid location if not then open the suggestions '''
		text = self.location_text.text.title()
		self.location_text.text = self.location_text.text.title()

		# Change the location to input text if it is a valid location
		if text in self.locations:
			self.change_location(self, text)
		elif text:
			self.suggestion_dropdown_open(text)

	def suggestion_dropdown_open(self, text):
		''' Open and populate the location dropdown with suggestions '''
		suggestions = self.give_location_suggestions(text)
		for i, key in enumerate(suggestions.keys()):
			if is_even(i):
				bg_color = constants.MAIN_COLOR
			else:
				bg_color = constants.SECONDRY_COLOR

			btn = LocationButton(text=suggestions[key], background_color=bg_color)
			btn.bind(on_release=lambda btn: self.suggestion_dropdown.select(btn.text))
			self.suggestion_dropdown.add_widget(btn)
		self.suggestion_dropdown.open(self.location_text)

	def give_location_suggestions(self, text):
		''' Use jaro-winkler algorithm to give location suggestions for the the input text '''
		suggestions = {}
		for location in self.locations:
			score = jaro_winkler(location, text)
			if score > 0.7:
				suggestions[score] = location
		keys = sorted(suggestions.keys(), reverse=True)

		return {key: suggestions[key] for key in keys}

	def change_location(self, instance, value):
		''' Change the location to the selected value and close the form '''

		self.app.change_location(value, *self.locations_data[value][3:])
		self.dismiss()
