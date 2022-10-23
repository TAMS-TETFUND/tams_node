from typing import Any, Dict, List
import PySimpleGUI as sg

import app.appconfigparser
from app.basegui import BaseGUIWindow
import app.windowdispatch
from app.serverconnection import ServerConnection
from app.guiutils import ValidationMixin
from app.nodedeviceinit import DeviceRegistration

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class NodeDeviceRegistrationWindow(ValidationMixin, BaseGUIWindow):
    """
    This window will be collect information for node device registration
    """
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        field_label_props = {"size": (22, 1)}
        input_props = {"size": (23, 1)}
        combo_props = {"size": 22}
        layout = [
            [sg.Push(), sg.Text("Admin Login Details"), sg.Push()],
            [sg.VPush()],
            [cls.message_display_field()],
            [
                sg.Text("Admin Username:", **field_label_props),
                sg.InputText(key=cls.key("admin_username"), **input_props),
            ],
            [
                sg.Text("Initial Password:", **field_label_props),
                sg.InputText(
                    key=cls.key("password"), password_char="*", **input_props
                ),
            ],
            [sg.Button("Submit", key=cls.key("submit"))],
            [sg.VPush()],
            cls.navigation_pane(),
        ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if DeviceRegistration.is_registered():
            cls.popup_auto_close_warn("Device already registered")
            window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event in (cls.key("home"), cls.key("back")):
            window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event in (cls.key("submit"), cls.key("next")):
            required_fields = [
                (values[cls.key("admin_username")], "Admin Username"),
                (values[cls.key("password")], "Password"),
            ]
            if (
                cls.validate_required_fields(required_fields, window)
                is not None
            ):
                return True

            conn = ServerConnection()
            try:
                conn.token_authentication(
                    username=values[cls.key("admin_username")],
                    password=values[cls.key("password")],
                )
            except Exception as e:
                cls.display_message("%s. %s" % (e, conn.server_url), window)
                return True
            try:
                DeviceRegistration.register_device()
            except Exception as e:
                cls.display_message(e, window)
                return True
            cls.popup_auto_close_success("Registered succesfully!")
            window_dispatch.dispatch.open_window("HomeWindow")
        return True

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        cls.hide_message_display_field(window)
        return super().refresh_dynamic_fields(window)