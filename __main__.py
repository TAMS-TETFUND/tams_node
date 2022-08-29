from app.appconfigparser import AppConfigParser
from app.windowdispatch import WindowDispatch, WindowDispatched
from app.initialloadingwindow import LoadingWindow


window_dispatch = WindowDispatched()
window_dispatch.open_window(LoadingWindow)
app_config = AppConfigParser()


# trying to speed up applicaton startup
# time by displaying a loading window as quickly as possible
import sys

from app.gui import main
from manage import django_setup


django_setup()
sys.path.append(".")

main()
