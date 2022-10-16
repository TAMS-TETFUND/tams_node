import sys

from manage import django_setup

from app.main import main_loop


sys.path.append(".")
django_setup()


main_loop()
