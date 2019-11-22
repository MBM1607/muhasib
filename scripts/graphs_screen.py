'''Module for prayer graph screen class and all the graphing functionality need to make the record graphs'''

from datetime import date as datetime_date, timedelta
from itertools import accumulate, chain

import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas
from kivy.metrics import dp
from kivy.properties import ObjectProperty, OptionProperty, StringProperty
from kivy.uix.screenmanager import Screen
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator

from constants import (GREY_COLOR, PRAYER_CATEGORY_COLORS,
					   PRAYER_CATEGORY_NAMES, PRAYER_NAMES)
from custom_widgets import ColorBoxLayout, CustomModalView
from helpers import notify

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


GRAPH_OPTIONS = ("Stacked Bar Graph", "Pie Graphs", "Bar Graphs")


class PrayerGraphsScreen(Screen):
	'''Screen for the record graphs'''
	start_date = ObjectProperty()
	end_date = ObjectProperty()
	graph = OptionProperty(GRAPH_OPTIONS[0], options=list(GRAPH_OPTIONS))

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.app = App.get_running_app()

		self.start_date.date = datetime_date.today() - timedelta(days=7)
		self.end_date.date = datetime_date.today()

	def get_prayer_data(self):
		'''Get the prayer data from the database'''

		results = [[0, 0, 0, 0] for _ in range(5)]
		records = self.app.database.get_prayer_record_range(self.start_date.date, self.end_date.date)

		# Calculate all prayer's activity throughout the range of dates
		for i, prayer in enumerate(chain(*records)):
			i = i % len(PRAYER_NAMES)
			j = PRAYER_CATEGORY_NAMES.index(prayer)
			results[i][j] += 1
		
		return results

	def create_graph(self):
		'''Create the popup with the graph and open it'''

		# Validate that the graph date data is valid and present
		if (self.end_date.text and self.start_date.text) and \
			(self.end_date.date > self.start_date.date):
			popup = GraphPopup()
			popup.create_graph(self.graph, self.get_prayer_data())
			popup.open()
		else:
			if not self.start_date.text and not self.end_date.text:
				message = "No value for start date and end date"
			elif not self.start_date.text:
				message = "No value for start date"
			elif not self.end_date.text:
				message = "No value for end date"
			elif self.end_date.date <= self.start_date.date:
				message = "End date is not greater than the start date"
			notify(title="Invalid Graph Data", message=message,mode="toast")


class GraphPopup(CustomModalView):
	'''Graph popup to show the graph made with the chosen data and the chosen type'''
	layout = ObjectProperty()
	title = StringProperty()
	
	def __init__(self,**kwargs):
		super().__init__(**kwargs)

		self.bind(on_dismiss=lambda _: self.destroy_graph())
	
	def destroy_graph(self):
		'''Remove the graph from the popup'''
		self.layout.remove_widget(self.figure)

	def create_graph(self, graph, results):
		'''Create the graph specified with the results and add it to layout'''
		if graph == "Bar Graphs":
			self.figure = create_record_bars_figure(results)
		elif graph == "Stacked Bar Graph":
			self.figure = create_record_stacked_bar_figure(results)
		elif graph == "Pie Graphs":
			self.figure = create_record_pie_graphs_figure(results)
		self.layout.add_widget(self.figure)
		self.title = graph


def create_pie_graphs(axes, sizes):
	'''Create pie graphs on all the axes'''
	for i, ax in enumerate(axes):
		_, _, autotext = ax.pie(sizes[i], colors=PRAYER_CATEGORY_COLORS,
								explode=(0.01, 0.01, 0.01, 0.01), autopct="")
		ax.axis("equal")
		ax.set_title(PRAYER_NAMES[i])
		for j, txt in enumerate(autotext):
			if sizes[i][j]:
				txt.set_text(f"{sizes[i][j]}")
				txt.set_color("white")

def create_bar_graphs(axes, sizes):
	'''Create bar graphs on all the axes'''

	for i, ax in enumerate(axes):

		# Create the bar and set the title
		ax.set_title(PRAYER_NAMES[i])
		ax.invert_yaxis()
		ax.barh(range(4), sizes[i], color=PRAYER_CATEGORY_COLORS)

		# Set the text size in the middle of the bar
		for y, (x, c) in enumerate(zip([x/2 for x in sizes[i]], sizes[i])):
			if c:
				ax.text(x, y, str(int(c)), ha='center', va='center', color='white')
		
		# Disable the ticks
		ax.set_yticklabels([])
		ax.set_xticklabels([])

def create_record_graphs_figure(graphing_function, prayer_data):
	'''Base function for creating five graphs with a legend aligned with it'''
	
	fig = plt.figure(constrained_layout=True)
	grid_spec = GridSpec(3, 2, figure=fig)
	fig.add_subplot(grid_spec[0, 1])
	fig.add_subplot(grid_spec[1, 0])
	fig.add_subplot(grid_spec[1, 1])
	fig.add_subplot(grid_spec[2, 0])
	fig.add_subplot(grid_spec[2, 1])

	graphing_function(fig.axes, prayer_data)
	
	# Create the legend of prayer categories for all the pie graphs and place it in the first axes
	ax = fig.add_subplot(grid_spec[0, 0])
	handles = [mpatches.Patch(color=PRAYER_CATEGORY_COLORS[i], label=PRAYER_CATEGORY_NAMES[i]) for i in range(4)]
	ax.legend(handles=handles, ncol=1, bbox_to_anchor=(0.5, 0.5), loc="center")
	ax.axis("off")

	return FigureCanvas(fig)

def create_record_pie_graphs_figure(prayer_data):
	'''Create five pie graphs displaying prayer data for each of the prayers'''
	return create_record_graphs_figure(create_pie_graphs, prayer_data)

def create_record_bars_figure(prayer_data):
	'''Create horizontal bar graphs displaying prayer data'''
	return create_record_graphs_figure(create_bar_graphs, prayer_data)

def create_record_stacked_bar_figure(prayer_data):
	'''Create a stacked horizontal bar graph displaying prayer data'''
	
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
