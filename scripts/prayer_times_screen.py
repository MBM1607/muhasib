''' Module to hold the class PrayerTimesScreen '''

from datetime import date, datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from constants import MAIN_COLOR, SECONDRY_COLOR


class PrayerTimesScreen(Screen):
	''' Class for the screen to show the prayer times '''
	times_list = ObjectProperty()
	prayer_time_left = ObjectProperty()
	next_prayer = ObjectProperty()
	current_time = ObjectProperty()
	location = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()

		self.bind(on_pre_enter=lambda _: self.create_prayers_data())
		self.bind(on_leave=lambda _: self.destroy_prayer_data())

	def create_prayers_data(self):
		''' Create the prayer times data and schedule the upgrade event '''
		self.update_prayer_times()
		
		self.update_clock_event = Clock.schedule_interval(lambda _: self.update_prayer_labels(), 30)
		self.location.text = self.app.settings["location"]

	def destroy_prayer_data(self):
		''' Remove all prayer data from the screen and cancel the upgrade event '''
		self.update_clock_event.cancel()
		self.times_data = {}
		self.times_list.data = []
		self.current_time.text = ""
		self.location.text = ""
		self.next_prayer.text = ""

	def update_prayer_times(self):
		''' Update the prayer times '''

		# Calculate today's prayer times
		self.times_data = self.app.prayer_times.get_times(date.today())

		# Populate the lists on the dashboard
		self.times_list.data = [{"name": n.capitalize(), "info": t} for n, t in self.times_data.items()]

		self.update_prayer_labels()

	def focus_next_prayer(self, next_prayer):
		''' Put focus on the next prayer so it can be highlighted'''
		for prayer in self.times_list.data:
			if prayer["name"] == next_prayer:
				prayer["background_color"] = SECONDRY_COLOR
			else:
				prayer["background_color"] = MAIN_COLOR

	def update_prayer_labels(self):
		''' Change the labels reporting information about prayers '''

		# Get just the current hour and minutes
		current_time = datetime.strptime(datetime.strftime(self.app.get_current_time(), "%H:%M"), "%H:%M")
		self.current_time.text = "Current Time: " + self.app.get_formatted_time(self.app.get_current_time())

		# Measure the time remaining in all prayers
		times_remaining = []
		for name, prayer_time in self.times_data.items():
			if self.app.prayer_times.time_format == "12h":
				prayer_time = datetime.strptime(prayer_time, "%I:%M %p")
			else:
				prayer_time = datetime.strptime(prayer_time, "%H:%M ")

			# If the prayer time is less than the current time then add a day to the answer so that the result is always positive
			if prayer_time < current_time:
				prayer_time += timedelta(1)

			dt = prayer_time - current_time
			times_remaining.append((dt, name, prayer_time))

		time_left, next_prayer, prayer_time = min(times_remaining, key=lambda times_remaining: times_remaining[0])
		time = (datetime.min + time_left).time()
		if time.hour == 0:
			self.prayer_time_left.text = time.strftime("%M minutes remaining")
		else:
			self.prayer_time_left.text = time.strftime("%H hours & %M minutes remaining")

		# Set the next prayer text
		self.next_prayer.text = next_prayer.capitalize() + ": " + self.app.get_formatted_time(prayer_time)

		# Put colored focus on the next prayer time
		self.focus_next_prayer(next_prayer.split(":")[0].capitalize())
