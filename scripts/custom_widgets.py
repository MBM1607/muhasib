''' Module for all the custom base widget classes '''

from itertools import chain

from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.recycleview import RecycleView
from kivy.lang.builder import Builder
from kivy.properties import ListProperty, StringProperty


class CustomButton(Button):
	''' Custom appearance for all buttons  '''
	background_color = ListProperty((26/255, 102/255, 38/255, 1))
	background_normal = ''

class CustomDropDown(DropDown):
	''' Custom appearance for all dropdowns  '''
	def __init__(self, **kwargs):
		super(CustomDropDown, self).__init__(**kwargs)
		self.container.spacing = 1
		self.container.padding = (0, 1, 0, 0)

class CustomLabel(Label):
	pass

class DoubleTextButton(ButtonBehavior, BoxLayout):
	''' Class used to show name and some other info '''
	name = StringProperty()
	info = StringProperty()
	background_color = ListProperty((26/255, 102/255, 38/255, 1))

class BlackLabel(CustomLabel):
	pass

class CustomModalView(ModalView):
	''' Custom Appearance for all modalviews  '''
	pass

class CustomPopup(Popup):
	''' Custom Appearance for all popups '''

class ItemsList(RecycleView):
	''' Class for various lists of items '''
	pass

Builder.load_file("scripts/custom_widgets.kv")