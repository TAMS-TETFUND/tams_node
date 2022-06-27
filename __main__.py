import sys
import os

from app.gui import main
from manage import django_setup

django_setup()
sys.path.append(".")

main()
