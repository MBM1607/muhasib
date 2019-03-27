''' Module for the location's form and all related functionality '''

import json

from kivy.properties import ObjectProperty
from kivy.app import App

from custom_widgets import CustomButton, CustomDropDown, CustomModalView

class LocationDropDown(CustomDropDown):
	''' Dropdown lists for countries and cities '''

	def dismiss(self):
		''' Clear children when dismissed '''
		self.clear_widgets()
		super().dismiss()


class LocationButton(CustomButton):
	pass

class LocationForm(CustomModalView):
	''' Class for location form to get user's city and country '''
	city_text = ObjectProperty()
	country_text = ObjectProperty()
	
	def __init__(self, **kwargs):
		super(LocationForm, self).__init__(**kwargs)
		self.app = App.get_running_app()
		
		with open("data/cities.json") as cities:
			self.cities = json.load(cities)
			self.countries = set(self.cities.keys())

		self.city_dropdown = LocationDropDown()
		self.country_dropdown = LocationDropDown()

		self.city_text.bind(on_text_validate=self.city_dropdown_open)
		self.city_dropdown.bind(on_select=self.change_city)
		self.country_text.bind(on_text_validate=self.country_dropdown_open)
		self.country_dropdown.bind(on_select=self.change_country)


	def city_dropdown_open(self, instance):
		''' Open and populate the city dropdown '''
		text = instance.text.title()
		self.city_text.text = self.city_text.text.title()
		self.country_text.text = self.country_text.text.title()

		if self.country_text.text in self.countries:
			for city in self.cities[self.country_text.text]:
				if city.startswith(text) and city != text:
					btn = LocationButton(text=city)
					btn.bind(on_release=lambda btn: self.city_dropdown.select(btn.text))
					self.city_dropdown.add_widget(btn)

			self.city_dropdown.open(instance)

	def change_city(self, instance, value):
		''' Change the city based on the value chosen on dropdown '''
		self.city_text.text = value
		self.set_location()

	def country_dropdown_open(self, instance):
		''' Open and populate the country dropdown '''
		text = instance.text.title()
		self.country_text.text = self.country_text.text.title()

		for country in self.countries:
			if country.startswith(text) and country != text:
				btn = LocationButton(text=country)
				btn.bind(on_release=lambda btn: self.country_dropdown.select(btn.text))
				self.country_dropdown.add_widget(btn)
		
		self.country_dropdown.open(instance)

	def change_country(self, instance, value):
		''' Change the country based on the value chosen on dropdown '''
		self.country_text.text = value

	def set_location(self):
		''' Set the location according to city and country specified and close location form '''
		if self.country_text.text in self.countries and self.city_text.text in self.cities[self.country_text.text]:
			self.app.location = [self.city_text.text, self.country_text.text]
			self.dismiss()

			with open("data/settings.json", "r") as json_file:
				location = json.load(json_file)
		
			location["location"] = self.app.location
			with open("data/settings.json", "w") as json_file:
				json.dump(location, json_file)
