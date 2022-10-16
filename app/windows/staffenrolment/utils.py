import json

import app.appconfigparser
from app.nodedevicedatasynch import NodeDataSynch
from app.basegui import BaseGUIWindow


app_config = app.appconfigparser.AppConfigParser()


def send_staff_data() -> None:
    """Synch staff data to the server.
    """
    try:
        message = NodeDataSynch.staff_register(
            app_config.cp.section_dict("new_staff")
        )
        BaseGUIWindow.popup_auto_close_success(message, duration=5)
        app_config.cp.remove_section("new_staff")
        # sync server data with the node device

    except Exception as e:
        error = json.loads(str(e))["detail"]
        BaseGUIWindow.popup_auto_close_error(error, duration=5)

    app_config.cp.remove_section("new_staff")
    return