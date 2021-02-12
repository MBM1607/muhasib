__all__ = ('FigureCanvasKivyAgg')

import six

import matplotlib
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import RendererBase, GraphicsContextBase,\
	FigureManagerBase, FigureCanvasBase
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backend_bases import register_backend, ShowBase

from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.base import EventLoop
from kivy.uix.floatlayout import FloatLayout
from kivy.core.image import Image
from backend_kivy import FigureCanvasKivy,\
							FigureManagerKivy, show, new_figure_manager,\
							NavigationToolbar2Kivy

register_backend('png', 'backend_kivyagg', 'PNG File Format')

toolbar = None
my_canvas = None


def new_figure_manager(num, *args, **kwargs):
	'''Create a new figure manager instance for the figure given.
	'''
	# if a main-level app must be created, this (and
	# new_figure_manager_given_figure) is the usual place to
	# do it -- see backend_wx, backend_wxagg and backend_tkagg for
	# examples. Not all GUIs require explicit instantiation of a
	# main-level app (egg backend_gtk, backend_gtkagg) for pylab
	FigureClass = kwargs.pop('FigureClass', Figure)
	thisFig = FigureClass(*args, **kwargs)
	return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
	'''Create a new figure manager instance and a new figure canvas instance
	   for the given figure.
	'''
	canvas = FigureCanvasKivyAgg(figure)
	manager = FigureManagerKivy(canvas, num)
	global my_canvas
	global toolbar
	toolbar = manager.toolbar.actionbar if manager.toolbar else None
	my_canvas = canvas
	return manager


class MPLKivyApp(App):
	'''Creates the App initializing a FloatLayout with a figure and toolbar
	   widget.
	'''
	figure = ObjectProperty(None)
	toolbar = ObjectProperty(None)

	def build(self):
		EventLoop.ensure_window()
		layout = FloatLayout()
		if self.figure:
			self.figure.size_hint_y = 0.9
			layout.add_widget(self.figure)
		if self.toolbar:
			self.toolbar.size_hint_y = 0.1
			layout.add_widget(self.toolbar)
		return layout


class Show(ShowBase):
	'''mainloop needs to be overwritten to define the show() behavior for kivy
	   framework.
	'''
	def mainloop(self):
		global my_canvas
		global toolbar
		app = App.get_running_app()
		if app is None:
			app = MPLKivyApp(figure=my_canvas, toolbar=toolbar)
			app.run()

show = Show()


class FigureCanvasKivyAgg(FigureCanvasKivy, FigureCanvasAgg):
	'''FigureCanvasKivyAgg class. See module documentation for more
	information.
	'''

	def __init__(self, figure, **kwargs):
		self.figure = figure
		self.bind(size=self._on_size_changed)
		super(FigureCanvasKivyAgg, self).__init__(figure=self.figure, **kwargs)
		self.img_texture = None
		self.img_rect = None
		self.blit()

	def draw(self):
		'''
		Draw the figure using the agg renderer
		'''
		self.canvas.clear()
		FigureCanvasAgg.draw(self)
		if self.blitbox is None:
			l, b, w, h = self.figure.bbox.bounds
			w, h = int(w), int(h)
			buf_rgba = self.get_renderer().buffer_rgba()
		else:
			bbox = self.blitbox
			l, b, r, t = bbox.extents
			w = int(r) - int(l)
			h = int(t) - int(b)
			t = int(b) + h
			reg = self.copy_from_bbox(bbox)
			buf_rgba = reg.to_string()
		texture = Texture.create(size=(w, h))
		texture.flip_vertical()
		color = self.figure.get_facecolor()
		with self.canvas:
			Color(*color)
			Rectangle(pos=self.pos, size=(w, h))
			Color(1.0, 1.0, 1.0, 1.0)
			self.img_rect = Rectangle(texture=texture, pos=self.pos,
									  size=(w, h))
		texture.blit_buffer(bytes(buf_rgba), colorfmt='rgba', bufferfmt='ubyte')
		self.img_texture = texture

	filetypes = FigureCanvasKivy.filetypes.copy()
	filetypes['png'] = 'Portable Network Graphics'

	def _on_pos_changed(self, *args):
		if self.img_rect is not None:
			self.img_rect.pos = self.pos

	def _print_image(self, filename, *args, **kwargs):
		'''Write out format png. The image is saved with the filename given.
		'''
		l, b, w, h = self.figure.bbox.bounds
		img = None
		if self.img_texture is None:
			texture = Texture.create(size=(w, h))
			texture.blit_buffer(bytes(self.get_renderer().buffer_rgba()),
								colorfmt='rgba', bufferfmt='ubyte')
			texture.flip_vertical()
			img = Image(texture)
		else:
			img = Image(self.img_texture)
		img.save(filename)

''' Standard names that backend.__init__ is expecting '''
FigureCanvas = FigureCanvasKivyAgg
FigureManager = FigureManagerKivy
NavigationToolbar = NavigationToolbar2Kivy
show = show
