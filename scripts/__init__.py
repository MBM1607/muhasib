'''Initializer function to convert to package

	and adding the current directory on path'''

from sys import path
from os.path import dirname, abspath

CURRENT_PATH = dirname(abspath(__file__))
path.append(CURRENT_PATH)