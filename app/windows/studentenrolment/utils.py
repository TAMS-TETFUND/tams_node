import json

from app.basegui import BaseGUIWindow
from app.nodedevicedatasynch import NodeDataSynch
import app.appconfigparser
import app.windowdispatch


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


def send_student_data() -> None:
    """Synch student data to the server."""
    try:
        message = NodeDataSynch.student_register(
            app_config.cp.section_dict("new_student")
        )
    except Exception as e:
        error = json.loads(str(e))["detail"]
        BaseGUIWindow.popup_auto_close_error(error, duration=5)
    else:
        BaseGUIWindow.popup_auto_close_success(message, duration=5)

    app_config.cp.remove_section("new_student")
    return
