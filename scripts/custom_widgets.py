''' Module for all the custom base widget classes '''

from itertools import chain

from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.recycleview import RecycleView
from kivy.lang.builder import Builder
from kivy.properties import ListProperty


class CustomButton(Button):
	background_color = ListProperty((26/255, 102/255, 38/255, 1))
	background_normal = ''

class CustomDropDown(DropDown):
	def __init__(self, **kwargs):
		super(CustomDropDown, self).__init__(**kwargs)
		self.container.spacing = 1
		self.container.padding = (0, 1, 0, 0)

class BlackLabel(Label):
	pass

class CustomModalView(ModalView):
	''' Base class for all the popups '''
	pass

class ItemsList(RecycleView):
	''' Class for various lists of items '''
	pass

class Gradient():
	''' Class to hold methods to make gradients '''
	@staticmethod
	def horizontal(*args):
		''' Make a horizontal gradient '''
		texture = Texture.create(size=(len(args), 1), colorfmt="rgba")
		buffer = bytes([ int(v)  for v in chain(*args) ])  # flattens
		texture.blit_buffer(buffer, colorfmt='rgba', bufferfmt='ubyte')
		return texture

	@staticmethod
	def vertical(*args):
		''' Make a vertical gradient '''
		texture = Texture.create(size=(1, len(args)), colorfmt="rgba")
		buffer = bytes([ int(v)  for v in chain(*args) ])  # flattens
		texture.blit_buffer(buffer, colorfmt='rgba', bufferfmt='ubyte')
		return texture

Builder.load_file("scripts/custom_widgets.kv")