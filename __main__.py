import sys

from manage import django_setup

from app.main import main_loop


django_setup()
sys.path.append(".")


main_loop()
