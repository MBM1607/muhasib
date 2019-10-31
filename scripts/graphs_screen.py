''' Module for prayer graph screen class and all the graphing functionality need to make the record graphs '''

from datetime import date as datetime_date
from itertools import accumulate, chain

import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas
from kivy.metrics import dp
from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.screenmanager import Screen
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator

from constants import (GREY_COLOR, PRAYER_CATEGORY_COLORS,
					   PRAYER_CATEGORY_NAMES, PRAYER_NAMES)
from custom_widgets import ColorBoxLayout
from helpers import get_previous_monday

# Enter the custom fonts into the matplotlib fonts list
font_files = mpl.font_manager.findSystemFonts(fontpaths="data/")
font_list = mpl.font_manager.createFontList(font_files)
mpl.font_manager.fontManager.ttflist.extend(font_list)

# Set the graphing styles
mpl.style.use("seaborn")
mpl.rcParams["font.family"] = "Saira"
mpl.rcParams["figure.facecolor"] = GREY_COLOR
mpl.rcParams['ytick.labelsize'] = dp(8)
mpl.rcParams['xtick.labelsize'] = dp(8)
mpl.rcParams['ytick.major.pad'] = 0


DATA_OPTIONS = ("Last Week", "Last Two Weeks", "Last Three Weeks", "Last Month")
GRAPH_OPTIONS = ("Bar Graph", "Pie Graph")


class PrayerGraphsScreen(Screen):
	''' Screen for the record graphs '''
	layout = ObjectProperty()
	graph_data = OptionProperty(DATA_OPTIONS[3], options=list(DATA_OPTIONS))
	graph = OptionProperty(GRAPH_OPTIONS[0], options=list(GRAPH_OPTIONS))

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.app = App.get_running_app()
		self.bind(on_pre_enter=lambda _: self.create_graph())
		self.bind(on_leave=lambda _: self.destroy_graph())

	def get_prayer_data(self, date):
		''' Get the prayer data from the  '''
		
		# Get the starting point date
		if self.graph_data == DATA_OPTIONS[0]:
			date = get_previous_monday(date)
		elif self.graph_data == DATA_OPTIONS[1]:
			date = get_previous_monday(date, weeks=1)
		elif self.graph_data == DATA_OPTIONS[2]:
			date = get_previous_monday(date, weeks=2)
		elif self.graph_data == DATA_OPTIONS[3]:
			date = datetime_date(date.year, date.month, 1)

		results = [[0, 0, 0, 0] for _ in range(5)]
		records = self.app.database.get_prayer_record_after(date)

		# Calculate all prayer's activity throughout the range of dates
		for i, prayer in enumerate(chain(*records)):
			i = i % len(PRAYER_NAMES)
			j = PRAYER_CATEGORY_NAMES.index(prayer)
			results[i][j] += 1
		
		return results
	
	def change_graph_data(self, value):
		''' Change the data used to create the graph and remake the graph with new data '''
		self.graph_data = value
		self.destroy_graph()
		self.create_graph()

	def change_graph(self, graph):
		''' Change the graph '''
		self.graph = graph
		self.destroy_graph()
		self.create_graph()

	def create_graph(self):
		''' Create the graph and add it to the layout '''
		results = self.get_prayer_data(self.app.today)
		if self.graph == "Bar Graph":
			self.figure = create_records_bar_figure(results)
		elif self.graph == "Pie Graph":
			self.figure = create_record_pie_graphs_figure(results)
		self.layout.add_widget(self.figure)

	def destroy_graph(self):
		''' Remove the graph from the layout '''
		self.layout.remove_widget(self.figure)
		self.figure = None


def create_pie_graphs(axes, sizes):
	''' Create pie graphs on all the axes '''
	for i, ax in enumerate(axes):
		_, _, autotext = ax.pie(sizes[i], colors=PRAYER_CATEGORY_COLORS,
								explode=(0.01, 0.01, 0.01, 0.01), autopct="")
		ax.axis("equal")
		ax.set_title(PRAYER_NAMES[i])
		for j, txt in enumerate(autotext):
			if sizes[i][j]:
				txt.set_text(f"{sizes[i][j]}")
				txt.set_color("white")

def create_record_pie_graphs_figure(prayer_data):
	''' Create five pie graphs displaying prayer data for each of the prayers '''


	fig = plt.figure(constrained_layout=True)
	grid_spec = GridSpec(3, 2, figure=fig)
	fig.add_subplot(grid_spec[0, 1])
	fig.add_subplot(grid_spec[1, 0])
	fig.add_subplot(grid_spec[1, 1])
	fig.add_subplot(grid_spec[2, 0])
	fig.add_subplot(grid_spec[2, 1])

	create_pie_graphs(fig.axes, prayer_data)
	
	# Create the legend of prayer categories for all the pie graphs and place it in the first axes
	ax = fig.add_subplot(grid_spec[0, 0])
	handles = [mpatches.Patch(color=PRAYER_CATEGORY_COLORS[i], label=PRAYER_CATEGORY_NAMES[i]) for i in range(4)]
	ax.legend(handles=handles, ncol=1, bbox_to_anchor=(0.5, 0.5), loc="center")
	ax.axis("off")

	return FigureCanvas(fig)

def create_records_bar_figure(prayer_data):
	''' Create a stacked horizontal bar graph displaying prayer data '''
	
	# Ready the data to be used to plot the graph
	data_cum = [list(accumulate(x)) for x in prayer_data]

	# Get the figure and the current axis to plot on
	fig, ax = plt.subplots()

	# Invert the yaxis so it starts from top instead of the bottom and set the x limit to the maximum value of records
	ax.invert_yaxis()
	ax.set_xlim(0, sum(max(prayer_data, key=sum)))

	# Make horizontal bars for all the categories
	for i, colname in enumerate(PRAYER_CATEGORY_NAMES):
		
		# Calculate the width of the bars and the starting coordinates of the bars 
		widths = [x[i] for x in prayer_data]
		accumul_data = [x[i] for x in data_cum]
		starts = [x - y for x, y in zip(accumul_data, widths)]

		# Calculate the horizontal centers of the current bars
		xcenters = [x + y / 2 for x, y in zip(starts, widths)]

		ax.barh(PRAYER_NAMES, widths, left=starts, height=0.5,
				label=colname, color=PRAYER_CATEGORY_COLORS[i])
		
		# Put the width number at the center of all bars
		for y, (x, c) in enumerate(zip(xcenters, widths)):
			if c:
				ax.text(x, y, str(int(c)), ha='center', va='center',
					color='white')
	
	ax.legend(ncol=len(PRAYER_CATEGORY_NAMES) // 2, bbox_to_anchor=(0, 1),
			loc='lower left')

	# Force the x-axis tick labels to be integars so decimal points aren't displayed on graphs
	ax.xaxis.set_major_locator(MaxNLocator(integer=True))

	return FigureCanvas(fig)
