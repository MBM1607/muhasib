''' Module to hold the class for the dashboard '''

from datetime import datetime, timedelta

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.app import App

from prayer_widgets import ItemsList

class Dashboard(BoxLayout):
	''' Class for the main screen of the app '''

	times_list = ObjectProperty()
	salah_list = ObjectProperty()
	current_prayer = ObjectProperty()
	prayer_time_left = ObjectProperty()
	next_prayer = ObjectProperty()
	location = ObjectProperty()
	qibla_direction = ObjectProperty()


	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
		self.app = App.get_running_app()
		self.location.text = self.app.location
		self.update_prayer_times()
	
	def update_prayer_times(self):
		''' Update the prayer times '''
		
		self.app.prayer_times.time_format = self.app.config.getdefault("Prayer Settings", "time_format", "24h")
		calc_method = self.app.config.getdefault("Prayer Settings", "calc_method", "Muslim World League")
		self.app.prayer_times.set_method(self.app.methods[calc_method])
		self.app.prayer_times.set_asr(self.app.config.getdefault("Prayer Settings", "asr_factor", "Standard"))

		times_data = self.app.prayer_times.get_times(self.app.today)
		self.update_prayer_labels(times_data)
		self.set_qibla_direction()
		
		# Populate the lists on the dashboard
		self.times_list.data = [{"name": n.capitalize(), "time": t} for n, t in times_data.items()]
		self.salah_list.data = [{"name": n.capitalize(), "time": t} for n, t in times_data.items() if n in ["fajr", "dhuhr", "asr", "maghrib", "isha"]]
		for x in self.salah_list.data:
			x["record"] = self.app.prayer_record[x["name"].lower()]

	def update_salah_buttons_record(self):
		''' Update the record of salah buttons '''

		for x in self.salah_list.children[0].children:
			x.record = self.app.prayer_record[x.name.lower()]


	def update_prayer_labels(self, times_data):
		''' Change the labels reporting information about prayers '''

		current_time = datetime.strptime(datetime.strftime(datetime.now(), "%H:%M"), "%H:%M")
		time_left = timedelta(24)
		current_prayer = ""
		next_prayer = ""
		prayer_names = list(times_data.keys())
		prayer_index = 0

		for n, t in times_data.items():
			if self.app.prayer_times.time_format == "12h":
				t = datetime.strptime(t, "%I:%M %p")
			else:
				t = datetime.strptime(t, "%H:%M ")

			if t < current_time:
				t += timedelta(1)

			dt = t - current_time
			if dt < time_left:
				time_left = dt
				current_prayer = prayer_names[prayer_index-1]
				next_prayer = n

			prayer_index += 1

		self.prayer_time_left.text = (datetime.min + time_left).time().strftime("%H:%M")	
		self.current_prayer.text = current_prayer.capitalize()
		self.next_prayer.text = next_prayer.capitalize()

	def set_qibla_direction(self):
		''' Set the qibla direction from current position '''

		qibla_direction = self.app.prayer_times.get_qibla()

		if qibla_direction < 0:
			self.qibla_direction.text = f"{abs(qibla_direction)} from North towards West"
		else:
			self.qibla_direction.text = f"{qibla_direction} from North towards East"
