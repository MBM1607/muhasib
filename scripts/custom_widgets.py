''' Module for all the custom base widget classes '''

from itertools import chain

from kivy.graphics import Rectangle
from kivy.properties import (BooleanProperty, ListProperty, ObjectProperty,
							 StringProperty, NumericProperty)
from kivy.metrics import dp
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView

import constants
from helpers import is_even


class ColorBoxLayout(BoxLayout):
	''' Layout with a background color '''
	background_color = ListProperty(constants.GREY_COLOR)


class BaseButton(ButtonBehavior, ColorBoxLayout):
	''' A base class for other types of custom buttons '''
	background_color = ListProperty(constants.MAIN_COLOR)
	background_normal = ''
	background_down = "data/button.png"
	border = ListProperty([16, 16, 16, 16])


class CustomButton(BaseButton, Label):
	''' A custom Button which is identical to the normal kivy button '''
	pass


class CustomActionBar(ColorBoxLayout):
	''' Class for a custom action bar '''
	background_color = ListProperty(constants.MAIN_COLOR)


class IconButton(ButtonBehavior, Image):
	''' Button with an icon instead of text '''
	icon = StringProperty()


class HorizontalIconTextButton(BaseButton):
	''' Button with an icon and text horizontally arranged '''
	icon = StringProperty()
	text = StringProperty()
	background_color = ListProperty(constants.MAIN_COLOR)


class VerticalIconTextButton(BaseButton):
	''' Buttton with an icon and text vertically arranged '''
	icon = StringProperty()
	text = StringProperty()
	background_color = ListProperty(constants.MAIN_COLOR)


class DoubleTextButton(BaseButton):
	''' A double labeled button to show name and some other info '''
	name = StringProperty()
	info = StringProperty()
	background_color = ListProperty(constants.MAIN_COLOR)


class LabelCheckBox(ColorBoxLayout):
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

		# Ensure that this is not the first loading before saving change to the database
		if self.base:
			self.base.change_extra_record(self.name.lower(), value)


class NavigationButton(IconButton):
	''' Button to open the navigation drawer.
			This button is used on all the screens, so it needs its own class'''
	pass


class NavigationWidget(ColorBoxLayout):
	''' Widget to be used as side panel in the navigation drawer '''
	pass


class CustomSpinner(CustomButton):
	''' Custom Appearance and implementation of the Spinner class of Kivy
	'''
	values = ListProperty()
	is_open = BooleanProperty(False)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.dropdown = DropDown()
		self.dropdown.bind(on_select=self.on_dropdown_select)
		self.bind(on_release=lambda _: self.open_dropdown())

	def close_dropdown(self):
		''' Close the dropdown if it is opened '''
		if self.dropdown.attach_to:
			self.is_open = False
			self.dropdown.dismiss()
	
	def open_dropdown(self):
		''' If the dropdown is not opened then open it '''
		if not self.dropdown.attach_to:
			self.is_open = True
			self.dropdown.open(self)

	def build_dropdown(self):
		''' Build the dropdown from the values '''
		for i, value in enumerate(self.values):
			item = CustomButton(size_hint_y=None, height=dp(48), text=value)
			if is_even(i):
				item.background_color = constants.TERNARY_COLOR
			else:
				item.background_color = constants.SECONDRY_COLOR

			item.bind(on_release=lambda option: self.dropdown.select(option.text))
			self.dropdown.add_widget(item)

	def on_values(self, instance, values):
		''' When values change then build dropdown from those values '''
		if self.dropdown.children:
			self.dropdown.clear_widgets()
		self.build_dropdown()

	def on_dropdown_select(self, instance, value):
		''' Select the value chosen from dropdown and close the dropdown '''
		self.text = value
		self.close_dropdown()


class CustomModalView(ModalView):
	''' Custom Appearance for all modalviews  '''
	pass


class CustomPopup(Popup):
	''' Custom Appearance for all popups '''
	pass


class CustomRecycleView(RecycleView):
	''' Custom Appearance settings for all recycle views '''
	pass


class WidgetGrid(CustomRecycleView):
	''' Class for various tables of widgets '''
	cols = NumericProperty(0)
