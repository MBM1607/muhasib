'''Module to hold the class for the dashboard'''

from custom_widgets import CustomScreen


class Dashboard(CustomScreen):
	'''Class for the main screen of the app'''

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
