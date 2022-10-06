import PySimpleGUI as sg

import app.appconfigparser
from app.basegui import BaseGUIWindow
import app.windowdispatch
from app.serverconnection import ServerConnection
from app.gui_utils import ValidationMixin
from app.nodedeviceinit import DeviceRegistration

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class NodeDeviceRegistrationWindow(ValidationMixin, BaseGUIWindow):
    """
    This window will be collect information for node device registration
    """

    @classmethod
    def window(cls):
        field_label_props = {"size": (22, 1)}
        input_props = {"size": (23, 1)}
        combo_props = {"size": 22}
        layout = [
            [sg.Push(), sg.Text("Node Details"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Server IP adress:", **field_label_props),
                sg.InputText(
                    key="server_ip_address",
                    default_text="127.0.0.1",
                    **input_props,
                ),
            ],
            [
                sg.Text("Server Port:", **field_label_props),
                sg.InputText(
                    key="server_port", default_text="8080", **input_props
                ),
            ],
            [
                sg.Text("Admin Username:", **field_label_props),
                sg.InputText(key="admin_username", **input_props),
            ],
            [
                sg.Text("Initial Password:", **field_label_props),
                sg.InputText(key="password", password_char="*", **input_props),
            ],
            [sg.Button("Submit", key="submit")],
            cls.navigation_pane(),
        ]

        window = sg.Window(
            "Node Registration Window", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("home", "back"):
            window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event in ("submit", "next"):
            required_fields = [
                (values["server_ip_address"], "Server IP address"),
                (values["server_port"], "Server port"),
                (values["admin_username"], "Admin Username"),
                (values["password"], "Password"),
            ]
            if (
                    cls.validate_required_fields(required_fields, window)
                    is not None
            ):
                return True

            conn = ServerConnection()
            conn.token_authentication(
                server_address=values["server_ip_address"],
                server_port=values["server_port"],
                username=values["admin_username"],
                password=values["password"],
            )
            DeviceRegistration.register_device(conn)
            cls.popup_auto_close_success("Registered succesfully!")
            window_dispatch.dispatch.open_window("HomeWindow")
        return True