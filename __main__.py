import sys
import os
import django

import tams_node
from app import gui

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tams_node.settings")
django.setup()
sys.path.append(".")

gui.main()
