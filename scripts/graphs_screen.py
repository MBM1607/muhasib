''' Module for prayer graph screen class and all the graphing functionality need to make the record graphs '''

from datetime import date as datetime_date
from itertools import accumulate

import matplotlib as mpl
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas
from kivy.metrics import dp
from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.screenmanager import Screen
from matplotlib.ticker import MaxNLocator

import constants
from custom_widgets import ColorBoxLayout
from helpers import get_previous_monday

# Enter the custom fonts into the matplotlib fonts list
font_files = mpl.font_manager.findSystemFonts(fontpaths="E:/Kivy/Muhasib/data/")
font_list = mpl.font_manager.createFontList(font_files)
mpl.font_manager.fontManager.ttflist.extend(font_list)

# Set the graphing styles
mpl.style.use("seaborn")
mpl.rcParams["font.family"] = "Saira"
mpl.rcParams["figure.facecolor"] = constants.GREY_COLOR
mpl.rcParams['ytick.labelsize'] = dp(8)
mpl.rcParams['xtick.labelsize'] = dp(8)
mpl.rcParams['ytick.major.pad'] = 0


GRAPHING_OPTIONS = ("Last Week", "Last Two Weeks", "Last Three Weeks", "Last Month")


class RecordGraphsScreen(Screen):
	''' Screen for the record graphs '''
	layout = ObjectProperty()
	spinner = ObjectProperty()
	graph_data = OptionProperty(GRAPHING_OPTIONS[3], options=list(GRAPHING_OPTIONS))

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.app = App.get_running_app()
		self.bind(on_pre_enter=lambda _: self.create_graph())
		self.bind(on_pre_leave=lambda _: self.destroy_graph())

	def get_prayer_data(self, date):
		''' Get the prayer data from the  '''
		
		# Get the starting point date
		if self.graph_data == GRAPHING_OPTIONS[0]:
			date = get_previous_monday(date)
		elif self.graph_data == GRAPHING_OPTIONS[1]:
			date = get_previous_monday(date, weeks=1)
		elif self.graph_data == GRAPHING_OPTIONS[2]:
			date = get_previous_monday(date, weeks=2)
		elif self.graph_data == GRAPHING_OPTIONS[3]:
			date = datetime_date(date.year, date.month, 1)

		results = [{"Group": 0, "Alone": 0, "Delayed": 0, "Not Prayed": 0} for _ in range(5)]
		records = self.app.database.get_prayer_record_after(date)

		# Calculate all prayer's activity throughout the range of dates
		for i, prayer in enumerate([x for record in records for x in record]):
			results[i % len(constants.PRAYER_NAMES)][prayer] += 1
		
		return results
	
	def change_graph_data(self, value):
		self.graph_data = value
		self.destroy_graph()
		self.create_graph()

	def create_graph(self):
		''' Create the graph and add it to the layout '''
		results = self.get_prayer_data(self.app.today)		
		self.figure = self.create_records_bar_figure(results)
		self.layout.add_widget(self.figure)

	def destroy_graph(self):
		''' Remove the graph from the layout '''
		self.layout.remove_widget(self.figure)
		self.figure = None

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

		# Force the x-axis tick labels to be integars so decimal points aren't displayed on graphs
		ax.xaxis.set_major_locator(MaxNLocator(integer=True))

		return FigureCanvas(fig)
