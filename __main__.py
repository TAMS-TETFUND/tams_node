import sys
import os

from app import gui
from manage import django_setup

django_setup()
sys.path.append(".")

gui.main()
