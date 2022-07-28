from app.windowdispatch import WindowDispatch
from app.initialloadingwindow import LoadingWindow


window_dispatch = WindowDispatch()
window_dispatch.open_window(LoadingWindow)


# trying to speed up applicaton startup
# time by displaying a loading window as quickly as possible
import sys

from app.gui import main
from manage import django_setup


django_setup()
sys.path.append(".")

main()
