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
	location = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()

	def on_pre_enter(self):
		''' Ready the screen for display and schedule upgrade event'''
		self.update_prayer_times()
		self.update_clock_event = Clock.schedule_interval(self.update_prayer_labels, 1)

	def on_pre_leave(self):
		''' Remove all data from the prayer times screen and remove the clock event '''
		self.update_clock_event.cancel()
		self.times_data = {}
		self.times_list.data = []

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

	def update_prayer_labels(self, wait=0.0):
		''' Change the labels reporting information about prayers '''
		current_time = datetime.strptime(datetime.strftime(datetime.now(), "%H:%M"), "%H:%M")
		time_left = timedelta(24)
		next_prayer = ""

		for n, t in self.times_data.items():
			if self.app.prayer_times.time_format == "12h":
				t = datetime.strptime(t, "%I:%M %p")
			else:
				t = datetime.strptime(t, "%H:%M ")

			if t < current_time:
				t += timedelta(1)

			dt = t - current_time
			if dt < time_left:
				time_left = dt
				if self.app.prayer_times.time_format == "12h":
					t = t.strftime("%I:%M %p")
				else:
					t = t.strftime("%H:%M")
				next_prayer = n + ": " + t


		time = (datetime.min + time_left).time()
		if time.hour == 0:
			self.prayer_time_left.text = time.strftime("%M minutes remaining")
		else:
			self.prayer_time_left.text = time.strftime("%H hours & %M minutes remaining")
		self.next_prayer.text = next_prayer.capitalize()

		# Put colored focus on the next prayer time
		self.focus_next_prayer(next_prayer.split(":")[0].capitalize())
