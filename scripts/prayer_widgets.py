''' Module to hold all of the various widgets used for setting and getting information about prayers '''

from datetime import date

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.button import ButtonBehavior

from constants import CATEGORY_COLORS_DICT
from custom_widgets import TextButton, CustomModalView, DoubleTextButton, LabelCheckBox


class PrayerOptions(CustomModalView):
	''' Popup to be display when a prayer button is released '''
	prayer = StringProperty()
	options_list = ObjectProperty()

	def __init__(self, prayer="", **kwargs):
		super().__init__(**kwargs)
		self.prayer = prayer.lower()

		self.bind(on_pre_open=lambda _: self.create_options_list())
		self.bind(on_dismiss=lambda _: self.destroy_options_list())
	
	def create_options_list(self):
		''' Add the prayer category data into the options list '''
		self.options_list.data = [{"text": name, "background_color": color}
									for name, color in CATEGORY_COLORS_DICT.items()]
	
	def destroy_options_list(self):
		''' Remove all data from prayer options list '''
		self.options_list.data = []


class PrayerOptionsButton(TextButton):
	''' Button to be used on prayer options popup'''
	def on_release(self):
		''' Change the prayer record according to the button pressed '''
		popup = self.parent.parent.parent.parent
		popup.attach_to.update_prayer_record(popup.prayer, self.text)
		popup.dismiss()


class ExtraRecordButton(LabelCheckBox):
	''' Button to show the current record of an extra record and allow changing of the record '''

	def on_active(self, instance, value):
		''' Change the record in the root's data list when activation status is changed '''

		super().on_active(instance, value)

		# Ensure that this is not the first loading before saving change to the database
		if self.parent:
			records_list = self.parent.parent.parent
			records_list.change_extra_record(self.name.lower(), value)


class SalahButton(DoubleTextButton):
	'''	Button to display the current prayer record and allow changing of the record '''

	def on_release(self):
		''' On button release open the popup '''
		self.parent.parent.parent.open_prayer_options(self.name)

	def on_info(self, instance, value):
		''' Color the button according to the way the prayer is performed '''
		self.background_color = CATEGORY_COLORS_DICT[value]


class RecordLists(BoxLayout):
	''' Class to dispaly a day's prayer and extra records and to provide and interface to change these records '''
	salah_record_list = ObjectProperty()
	extra_record_list = ObjectProperty()

	def __init__(self, date=date.today(), **kwargs):
		super().__init__(**kwargs)
		self.database = App.get_running_app().database
		self.date = date
		self.prayer_record = {}
		self.extra_record = {}

	def create_lists(self):
		''' Create and populate the record lists from the record extracted from the database '''
		self.database.create_record(self.date)
		record = self.database.get_record(self.date)

		self.prayer_record = {"fajr": record[0], "dhuhr": record[1], "asr": record[2],
							"maghrib": record[3], "isha": record[4]}

		# If fast is required then display fast record button
		if record[5]:
			self.extra_record["fast"] = record[6]

		self.extra_record = {"quran": record[7], "hadees": record[8]}

		self.salah_record_list.data = [{"name": n.capitalize(), "info": r} for n, r in self.prayer_record.items()]
		self.extra_record_list.data = [{"name": n.capitalize(), "active": r} for n, r in self.extra_record.items()]
	
	def destroy_lists(self):
		''' Destroy the record lists '''
		self.prayer_record = {}
		self.extra_record = {}
		self.salah_record_list.data = []
		self.extra_record_list.data = []

	def change_extra_record(self, name, value):
		''' Update the extra records and save to database. '''
		self.extra_record[name] = int(value)
		self.database.update_record(self.date, **self.prayer_record, **self.extra_record)

	def update_prayer_record(self, name, value):
		''' Update the prayer records and save it to database. '''
		self.prayer_record[name] = value
		self.update_prayer_list(name, value)
		self.database.update_record(self.date, **self.prayer_record, **self.extra_record)	

	def update_prayer_list(self, prayer, record):
		''' Change the prayer record for the provided prayer '''
		for child in self.salah_record_list.children[0].children:
			if child.name.lower() == prayer:
				child.info = record

	def open_prayer_options(self, prayer):
		''' Open the prayer options popup '''
		PrayerOptions(prayer=prayer, attach_to=self).open()
