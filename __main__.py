import sys

from manage import django_setup

from app.main import main_loop
import app.appconfigparser
from app.gui_utils import update_device_op_mode


django_setup()
sys.path.append(".")

# setting the operational mode of device
app_config = app.appconfigparser.AppConfigParser()
app_config.cp["tmp_settings"] = {}
update_device_op_mode()


main_loop()
