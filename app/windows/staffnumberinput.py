from typing import Any, Dict, List, Optional
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.guiutils import StaffBiometricVerificationRouterMixin, ValidationMixin
import app.appconfigparser
import app.windowdispatch
from db.models import Staff

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffNumberInputWindow(
    ValidationMixin, StaffBiometricVerificationRouterMixin, BaseGUIWindow
):
    """This window will provide an on-screen keypad for staff to enter
    their staff id/number by button clicks."""
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        INPUT_BUTTON_SIZE = (8, 2)
        input_button_dict = {
            "s": (7, 2),
            "button_color": cls.BUTTON_COLOR,
            "font": ('Any', 12, 'bold'),
            "border_width": 0,
        }
        column1 = [
            [
                sg.Button("1", k=cls.key("1"), **input_button_dict),
                sg.Button("2", k=cls.key("2"), **input_button_dict),
                sg.Button("3", k=cls.key("3"), **input_button_dict),
                sg.Button("0", k=cls.key("0"), **input_button_dict),
            ],
            [
                sg.Button("4", k=cls.key("4"), **input_button_dict),
                sg.Button("5", k=cls.key("5"), **input_button_dict),
                sg.Button("6", k=cls.key("6"), **input_button_dict),
                sg.Button("/", k=cls.key("/"), **input_button_dict),
            ],
            [
                sg.Button("7", k=cls.key("7"), **input_button_dict),
                sg.Button("8", k=cls.key("8"), **input_button_dict),
                sg.Button("9", k=cls.key("9"), **input_button_dict),
                sg.Button("AC", k=cls.key("clear"), **input_button_dict),
            ],
            [
                sg.Push(),
                sg.Button("Submit", key=cls.key("submit"), s=INPUT_BUTTON_SIZE),
                sg.Push(),
            ],
        ]

        layout = [
            [sg.VPush()],
            [cls.message_display_field()],
            [
                sg.Push(),
                sg.Text("Staff Number:    SS."),
                sg.Input(
                    size=(15, 1),
                    justification="left",
                    key=cls.key("staff_number_input"),
                    focus=True,
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Column(column1), sg.Push()],
            [sg.VPush()],
            cls.navigation_pane(),
        ]
        scrolled_layout = [
            [
                sg.Column(
                    layout,
                    scrollable=True,
                    vertical_scroll_only=True,
                    expand_y=True,
                    key=cls.key("main_column"),
                )
            ]
        ]
        return scrolled_layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event in ("back", "home"):
            cls.back_nav_key_handler()
            return True

        keys_pressed = None
        if event in (
            cls.key("0"),
            cls.key("1"),
            cls.key("2"),
            cls.key("3"),
            cls.key("4"),
            cls.key("5"),
            cls.key("6"),
            cls.key("7"),
            cls.key("8"),
            cls.key("9"),
        ):
            keys_pressed = values[cls.key("staff_number_input")]
            keys_pressed += event.strip(cls.key_prefix())
            window[cls.key("staff_number_input")].update(keys_pressed)
            return True

        elif event == cls.key("clear"):
            window[cls.key("staff_number_input")].update("")
            cls.hide_message_display_field(window)
            cls.resize_column(window)
            return True

        elif event in (cls.key("back"), cls.key("home")):
            cls.back_nav_key_handler()

        elif event in (cls.key("submit"), cls.key("next")):
            if cls.validate(values, window) is not None:
                return True
            keys_pressed = values[cls.key("staff_number_input")]
            staff_number_entered = "SS." + keys_pressed
            staff = Staff.objects.filter(staff_number=staff_number_entered)

            if not staff.exists():
                cls.popup_auto_close_error(
                    "No staff found with given staff ID. "
                    "\nEnsure you have been duly registered on the system.",
                    duration=5,
                )
                return True
            cls.process_staff(staff)
        return True

    @classmethod
    def validate(
        cls, values: Dict[str, Any], window: sg.Window
    ) -> Optional[bool]:
        """Validate values supplied by user in the window input fields."""
        for val_check in (
            cls.validate_required_field(
                (values[cls.key("staff_number_input")], "staff number")
            ),
            cls.validate_staff_number(
                "SS." + values[cls.key("staff_number_input")]
            ),
        ):
            if val_check is not None:
                cls.popup_auto_close_error(val_check)
                return True
        return None

    @classmethod
    def resize_column(cls, window: sg.Window) -> None:
        """Refresh GUI when adding/removing message display field."""
        window.refresh()
        window[cls.key("main_column")].contents_changed()

    @classmethod
    def process_staff(cls, staff: Staff) -> None:
        """Process staff info for update."""
        app_config.cp["tmp_staff"] = app_config.cp.dict_vals_to_str(
            staff.values(
                "staff_number",
                "first_name",
                "last_name",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )
        cls.staff_verification_window()
        return

    @staticmethod
    def back_nav_key_handler() -> None:
        """Handle user pressing back button in nav pane."""
        window_dispatch.dispatch.open_window("HomeWindow")
        return
