from app.appconfigparser import AppConfigParser
import app.windowdispatch
from app.initialloadingwindow import LoadingWindow


# window_dispatch = app.windowdispatch.WindowDispatch()
# window_dispatch.dispatch.open_window("LoadingWindow")
# app_config = AppConfigParser()

# trying to speed up applicaton startup
# time by displaying a loading window as quickly as possible
import sys

from app.main import main
from manage import django_setup


django_setup()
sys.path.append(".")

main()
