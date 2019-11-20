'''Module for all the custom base widget classes'''

from itertools import chain

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, ListProperty, NumericProperty,
							 StringProperty)
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.recycleview import RecycleView
from kivy.uix.textinput import TextInput

import constants
from helpers import is_even


class ColorBoxLayout(BoxLayout):
	'''Layout with a background color'''
	background_color = ListProperty(constants.GREY_COLOR)


class BaseButton(ButtonBehavior, ColorBoxLayout):
	'''A base class for other types of custom buttons'''
	background_color = ListProperty(constants.MAIN_COLOR)
	background_normal = ''
	background_down = "data/button.png"
	border = ListProperty([16, 16, 16, 16])


class TextButton(BaseButton, Label):
	'''A custom Button which is identical to the normal kivy button'''
	pass


class CustomActionBar(ColorBoxLayout):
	'''Class for a custom action bar'''
	background_color = ListProperty(constants.MAIN_COLOR)


class ScreenActionBar(CustomActionBar):
	'''Action Bar with navigation button and text for the screens'''
	text = StringProperty()


class IconButton(ButtonBehavior, Image):
	'''Button with an icon instead of text'''
	icon = StringProperty()


class HorizontalIconTextButton(BaseButton):
	'''Button with an icon and text horizontally arranged'''
	icon = StringProperty()
	text = StringProperty()
	background_color = ListProperty(constants.MAIN_COLOR)


class VerticalIconTextButton(BaseButton):
	'''Buttton with an icon and text vertically arranged'''
	icon = StringProperty()
	text = StringProperty()
	background_color = ListProperty(constants.MAIN_COLOR)


class DoubleTextButton(BaseButton):
	'''A double labeled button to show name and some other info'''
	name = StringProperty()
	info = StringProperty()
	background_color = ListProperty(constants.MAIN_COLOR)


class LabelCheckBox(BaseButton):
	'''Checkbox with its very own label in a colored layout'''
	name = StringProperty()
	active = BooleanProperty(False)
	checkbox_on = StringProperty()
	checkbox_off = StringProperty()
	unactive_color = ListProperty(constants.WARNING_COLOR)
	active_color = ListProperty(constants.SECONDRY_COLOR)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_press=lambda _: self.toggle_state())

	def toggle_state(self):
		'''toggle the acitvation state of the button'''
		self.active = not self.active


class SideBarButton(HorizontalIconTextButton):
	'''Button for the sidebar navigation'''
	screen = StringProperty()


class DashboardButton(VerticalIconTextButton):
	'''Button to be used on the dashboard'''
	screen = StringProperty()


class NavigationWidget(ColorBoxLayout):
	'''Widget to be used as side panel in the navigation drawer'''
	pass


class CustomTextInput(TextInput):
	'''Custom Appearance for the Text Input Widget'''
	pass


class CustomSpinner(TextButton):
	'''Custom Appearance and implementation of the Spinner class of Kivy'''
	values = ListProperty()
	is_open = BooleanProperty(False)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.dropdown = DropDown()
		self.dropdown.bind(on_select=self.on_dropdown_select)
		self.bind(on_release=lambda _: self.open_dropdown())

	def close_dropdown(self):
		'''Close the dropdown if it is opened'''
		if self.dropdown.attach_to:
			self.is_open = False
			self.dropdown.dismiss()

	def open_dropdown(self):
		'''If the dropdown is not opened then open it'''
		if not self.dropdown.attach_to:
			self.is_open = True
			self.dropdown.open(self)

	def build_dropdown(self):
		'''Build the dropdown from the values'''
		for i, value in enumerate(self.values):
			item = TextButton(size_hint_y=None, height=dp(48), text=value)
			if is_even(i):
				item.background_color = constants.TERNARY_COLOR
			else:
				item.background_color = constants.SECONDRY_COLOR

			item.bind(on_release=lambda option: self.dropdown.select(option.text))
			self.dropdown.add_widget(item)

	def on_values(self, instance, values):
		'''When values change then build dropdown from those values'''
		if self.dropdown.children:
			self.dropdown.clear_widgets()
		self.build_dropdown()

	def on_dropdown_select(self, instance, value):
		'''Select the value chosen from dropdown and close the dropdown'''
		self.text = value
		self.close_dropdown()


class CustomModalView(ModalView):
	'''Custom Appearance for all modalviews'''
	pass


class LoadingPopup(CustomModalView):
	'''Popup to display while data is loading'''
	text = StringProperty("Loading ...")


class CustomRecycleView(RecycleView):
	'''Custom Appearance settings for all recycle views'''
	pass


class WidgetGrid(CustomRecycleView):
	'''Class for various tables of widgets'''
	cols = NumericProperty(0)
