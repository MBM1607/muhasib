''' Module for all the custom base widget classes '''

from itertools import chain

import constants
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.properties import (BooleanProperty, ListProperty, ObjectProperty,
                             StringProperty)
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView


class CustomActionBar(BoxLayout):
	pass


class CustomButton(Button):
	''' Custom appearance for all buttons  '''
	background_color = ListProperty(constants.MAIN_COLOR)
	background_normal = ''
	background_down = "data/button.png"


class CustomDropDown(DropDown):
	''' Custom appearance for all dropdowns  '''
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.container.spacing = 1
		self.container.padding = (0, 1, 0, 0)


class CustomLabel(Label):
	pass


class DoubleTextButton(ButtonBehavior, BoxLayout):
	''' A double labeled button to show name and some other info '''
	name = StringProperty()
	info = StringProperty()
	background_color = ListProperty(constants.MAIN_COLOR)

class LabelCheckBox(BoxLayout):
	''' Checkbox with its very own label in a colored layout ''' 
	name = StringProperty()
	active = BooleanProperty(False)
	base = ObjectProperty()
	background_color = ListProperty(constants.WARNING_COLOR)

	def on_active(self, instance, value):
		''' When check box is clicked change the value in the record and the color '''

		if value:
			self.background_color = constants.SECONDRY_COLOR
		else:
			self.background_color = constants.WARNING_COLOR
		# Ensure that this is not the first loading	
		if self.base:
			self.base.change_extra_record(self.name.lower(), value)

class BlackLabel(CustomLabel):
	''' Yeah this is exactly what you think it is.'''
	pass


class CustomModalView(ModalView):
	''' Custom Appearance for all modalviews  '''
	pass


class CustomPopup(Popup):
	''' Custom Appearance for all popups '''


class ItemsList(RecycleView):
	''' Class for various lists of items '''
	pass
