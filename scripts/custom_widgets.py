''' Module for all the custom base widget classes '''

from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.lang.builder import Builder

Builder.load_file("scripts/custom_widgets.kv")


class CustomButton(Button):
	pass


class CustomDropDown(DropDown):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.container.spacing = 1
		self.container.padding = (0, 1, 0, 0)


class BlackLabel(Label):
	pass


class Empty(Widget):
	''' Empty spot on the calendar '''
	pass

class CustomPopup(Popup):
	''' Base class for all the popups '''
	pass

class ItemsList(RecycleView):
	''' Class for various lists of items '''
	pass
