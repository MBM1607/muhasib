''' Module for prayer graph screen class and all the graphing functionality need to make the record graphs '''

from itertools import accumulate

from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib as mpl

import constants
from custom_widgets import ColorBoxLayout

# Enter the custom fonts into the matplotlib fonts list
font_files = font_manager.findSystemFonts(fontpaths="E:/Kivy/Muhasib/data/")
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)

# Set the graphing styles
mpl.style.use("seaborn")
mpl.rcParams["font.family"] = "Saira"
mpl.rcParams["figure.facecolor"] = constants.GREY_COLOR
mpl.rcParams['ytick.labelsize'] = dp(8)
mpl.rcParams['xtick.labelsize'] = dp(8)
mpl.rcParams['ytick.major.pad'] = 0

class RecordGraphsScreen(Screen):
	''' Screen for the record graphs '''
	layout = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.app = App.get_running_app()

	def get_prayer_data(self, date):
		results = [
					{"Group": 0, "Alone": 0, "Delayed": 0, "Not Prayed": 0},
					{"Group": 0, "Alone": 0, "Delayed": 0, "Not Prayed": 0},
					{"Group": 0, "Alone": 0, "Delayed": 0, "Not Prayed": 0},
					{"Group": 0, "Alone": 0, "Delayed": 0, "Not Prayed": 0},
					{"Group": 0, "Alone": 0, "Delayed": 0, "Not Prayed": 0}
				]
		record = self.app.database.get_record(date)[:5]
		for i, prayer in enumerate(record):
			results[i][prayer] += 1
		return results
		
	def on_pre_enter(self):
		''' Create the graph and ready the screen to be displayed '''
		results = self.get_prayer_data(self.app.today)
		
		self.figure = self.create_records_bar_figure(results)

		self.layout.add_widget(self.figure)

	def on_pre_leave(self):
		''' Remove all data from the screen before leaving it '''
		self.layout.remove_widget(self.figure)

	@staticmethod
	def create_records_bar_figure(prayer_data):
		''' Create a stacked horizontal bar graph displaying prayer data for the chosen number of days'''
		
		# Ready the data to be used to plot the graph
		data = [list(x.values()) for x in prayer_data]
		data_cum = [list(accumulate(x)) for x in data]

		# Get the figure and the current axis to plot on
		fig, ax = plt.subplots()

		# Invert the yaxis so it starts from top instead of the bottom and set the x limit to the maximum value of records
		ax.invert_yaxis()
		ax.set_xlim(0, sum(max(data, key=sum)))

		# Make horizontal bars for all the categories
		for i, colname in enumerate(constants.PRAYER_CATEGORY_NAMES):
			
			# Calculate the width of the bars and the starting coordinates of the bars 
			widths = [x[i] for x in data]
			accumul_data = [x[i] for x in data_cum]
			starts = [x - y for x, y in zip(accumul_data, widths)]

			# Calculate the horizontal centers of the current bars
			xcenters = [x + y / 2 for x, y in zip(starts, widths)]


			ax.barh(constants.PRAYER_NAMES, widths, left=starts, height=0.5,
					label=colname, color=constants.PRAYER_CATEGORY_COLORS[colname])
			
			# Put the width number at the center of all bars
			for y, (x, c) in enumerate(zip(xcenters, widths)):
				if c:
					ax.text(x, y, str(int(c)), ha='center', va='center',
						color='white')
		
		ax.legend(ncol=len(constants.PRAYER_CATEGORY_NAMES) // 2, bbox_to_anchor=(0, 1),
				loc='lower left')

		return FigureCanvas(fig)
