from typing import Any, Dict
import time

import PySimpleGUI as sg
from app.basegui import BaseGUIWindow
from app.gui_utils import ValidationMixin
from app.networkinterface import WLANInterface
from app.nodedevicedatasynch import NodeDataSynch
import app.appconfigparser
import app.windowdispatch


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class ServerConnectionDetailsWindow(ValidationMixin, BaseGUIWindow):
    """
    This window will be collect information (server address, SSID, password)
    that will enable connection to the server.
    """

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        field_label_props = {"size": (22, 1)}
        input_props = {"size": (23, 1)}
        combo_props = {"size": 22}
        layout = [
            [sg.Push(), sg.Text("Server Details"), sg.Push()],
            [cls.message_display_field()],
            [sg.VPush()],
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
                sg.Text("Connection Type:", **field_label_props),
                sg.Combo(
                    values=["WiFi", "LORA"],
                    default_value="WiFi",
                    key="connection_type",
                    enable_events=True,
                    **combo_props,
                ),
            ],
            [
                sg.Text("WLAN Name (SSID):", **field_label_props),
                sg.Combo(
                    key="ssid",
                    values=WLANInterface.available_networks() or [],
                    **combo_props,
                ),
            ],
            [
                sg.Text("WLAN Password:", **field_label_props),
                sg.InputText(
                    key="wlan_password", password_char="*", **input_props
                ),
            ],
            [sg.Button("Submit", key="submit")],
            [sg.VPush()],
            cls.navigation_pane(),
        ]

        window = sg.Window(
            "Server Details Window", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
        """Track user interaction with window."""
        if event in ("home", "back"):
            window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event == "connection_type":
            if values["connection_type"] != "WiFi":
                window["ssid"].disabled = True
                window["wlan_password"].disabled = True
            else:
                window["ssid"].disabled = False
                window["wlan_password"].disabled = False

        if event in ("submit", "next"):
            required_fields = [
                (values["server_ip_address"], "Server IP address"),
                (values["server_port"], "Server port"),
            ]

            # TODO: not validating all required fields. Only validating the first field
            if (
                cls.validate_required_fields(required_fields, window)
                is not None
            ):
                return True

            app_config.cp["server_details"] = {
                "server_ip_address": values["server_ip_address"],
                "server_port": values["server_port"],
                "connection_type": values["connection_type"],
                "ssid": values["ssid"],
                "wlan_password": values["wlan_password"],
            }

            server_details = app_config.cp["server_details"]
            if values["connection_type"] == "WiFi":
                try:
                    connect_result = 0
                    # TODO: uncomment and fix the connect to wifi method
                    # connect_result = connect_to_wifi(
                    #     server_details["ssid"], server_details["wlan_password"]
                    # )
                except Exception as e:
                    cls.popup_auto_close_error(e)
                    connect_result = 0  # TODO: remove this flag  and uncomment return value when done testing
                    # return True

                if connect_result == 0:
                    cls.popup_auto_close_success(
                        "WiFi network connection established"
                    )
                    time.sleep(1)
                    NodeDataSynch.start_data_sync()

                elif connect_result != 0:
                    cls.popup_auto_close_error(
                        "Error establishing WiFi Network connection. Check details provided."
                    )
                    return True

                # test connection to server after network has been established
        return True