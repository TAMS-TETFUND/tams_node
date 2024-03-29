from typing import Any, Dict, List
import time

import PySimpleGUI as sg
from app.basegui import BaseGUIWindow
from app.guiutils import ValidationMixin
from app.networkinterface import WLANInterface
from app.serverconnection import ServerConnection
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
    __slots__ = ()
    
    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        field_label_props = {"size": (22, 1)}
        input_props = {"size": (23, 1)}
        combo_props = {"size": 22}
        server_details = {}
        if app_config.cp.has_section("server_details"):
            server_details = app_config.cp["server_details"]
        layout = [
            [sg.Push(), sg.Text("Server Details"), sg.Push()],
            [cls.message_display_field()],
            [sg.VPush()],
            [
                sg.Text("Server IP adress:", **field_label_props),
                sg.InputText(
                    key=cls.key("server_ip_address"),
                    default_text=server_details["server_ip_address"]
                    if server_details
                    else "127.0.0.1",
                    **input_props,
                ),
            ],
            [
                sg.Text("Server Port:", **field_label_props),
                sg.InputText(
                    key=cls.key("server_port"),
                    default_text=server_details["server_port"]
                    if server_details
                    else "8080",
                    **input_props,
                ),
            ],
            [
                sg.Text("Connection Type:", **field_label_props),
                sg.Combo(
                    values=["WiFi", "LORA"],
                    default_value=server_details["connection_type"]
                    if server_details
                    else "WiFi",
                    key=cls.key("connection_type"),
                    enable_events=True,
                    **combo_props,
                ),
            ],
            [
                sg.Text("WLAN Name (SSID):", **field_label_props),
                sg.Combo(
                    key=cls.key("ssid"),
                    default_value=server_details["ssid"]
                    if server_details
                    else "",
                    values=WLANInterface.available_networks() or [],
                    **combo_props,
                ),
            ],
            [
                sg.Text("WLAN Password:", **field_label_props),
                sg.InputText(
                    key=cls.key("wlan_password"),
                    default_text=server_details["wlan_password"]
                    if server_details
                    else "",
                    password_char="*",
                    **input_props,
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

        # Don't open window if server connection already established
        if ServerConnection().test_connection():
            if app_config.cp.has_option("server_connection", "next_window"):
                window_dispatch.dispatch.open_window(
                    app_config.cp.get("server_connection", "next_window")
                )
                app_config.cp.remove_section("server_connection")
            else:
                window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event in (cls.key("home"), cls.key("back")):
            window_dispatch.dispatch.open_window("HomeWindow")
            return True

        if event == cls.key("connection_type"):
            if values[cls.key("connection_type")] != "WiFi":
                window[cls.key("ssid")].disabled = True
                window[cls.key("wlan_password")].disabled = True
            else:
                window[cls.key("ssid")].disabled = False
                window[cls.key("wlan_password")].disabled = False

        if event in (cls.key("submit"), cls.key("next")):
            required_fields = [
                (values[cls.key("server_ip_address")], "Server IP address"),
                (values[cls.key("server_port")], "Server port"),
            ]

            # TODO: not validating all required fields. Only validating the first field
            if (
                cls.validate_required_fields(required_fields, window)
                is not None
            ):
                return True

            app_config.cp["server_details"] = {
                "server_ip_address": values[cls.key("server_ip_address")],
                "server_port": values[cls.key("server_port")],
                "connection_type": values[cls.key("connection_type")],
                "ssid": values[cls.key("ssid")],
                "wlan_password": values[cls.key("wlan_password")],
            }

            server_details = app_config.cp["server_details"]
            if values[cls.key("connection_type")] == "WiFi":
                # check if server address is the local device.
                if values[cls.key("server_ip_address")].lower() in (
                    "localhost",
                    "127.0.0.1",
                ):
                    connect_result = 0
                else:
                    try:
                        connect_result = WLANInterface.connect_to_wifi(
                            server_details["ssid"],
                            server_details["wlan_password"],
                        )
                    except Exception as e:
                        cls.popup_auto_close_error(e)
                        return True

                if connect_result != 0:
                    cls.popup_auto_close_error(
                        "Error establishing WiFi network connection. Check details provided."
                    )
                    return True

                conn = ServerConnection()
                conn.server_address = values[cls.key("server_ip_address")]
                conn.server_port = values[cls.key("server_port")]

                if not conn.test_connection():
                    cls.display_message(
                        "Server not reachable with provided IP/Port.", window
                    )
                    return True

                cls.popup_auto_close_success(
                    "WiFi network connection established"
                )
                time.sleep(1)
                if app_config.cp.has_option("server_connection", "next_window"):
                    window_dispatch.dispatch.open_window(
                        app_config.cp.get("server_connection", "next_window")
                    )
                    app_config.cp.remove_section("server_connection")
                    return True
        return True

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        cls.hide_message_display_field(window)
        return super().refresh_dynamic_fields(window)