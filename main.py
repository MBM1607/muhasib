""" Main python file for running and defining the app object. """

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import ObjectProperty


class Dashboard(BoxLayout):
	""" Class for the main screen of the app """

	salah_buttons_list = ObjectProperty()


class SalahButton(ListItemButton):
	pass

class MuhasibApp(App):
	""" Muhasib app object"""
	
	def build(self):
		return Dashboard()


if __name__ == "__main__":
	MuhasibApp().run()