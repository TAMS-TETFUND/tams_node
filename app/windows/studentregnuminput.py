from typing import Any, Dict, Optional
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.guiutils import (
    ValidationMixin,
    StudentBiometricVerificationRouterMixin,
)
from db.models import AttendanceRecord, Student, RecordTypesChoices

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentRegNumInputWindow(
    ValidationMixin, StudentBiometricVerificationRouterMixin, BaseGUIWindow
):
    """Window provides an interface for students to enter their registration
    numbers by button clicks."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        INPUT_BUTTON_SIZE = (8, 2)
        column1 = [
            [
                sg.Button("1", s=INPUT_BUTTON_SIZE, k=cls.key("1")),
                sg.Button("2", s=INPUT_BUTTON_SIZE, k=cls.key("2")),
                sg.Button("3", s=INPUT_BUTTON_SIZE, k=cls.key("3")),
                sg.Button("0", s=INPUT_BUTTON_SIZE, k=cls.key("0")),
            ],
            [
                sg.Button("4", s=INPUT_BUTTON_SIZE, k=cls.key("4")),
                sg.Button("5", s=INPUT_BUTTON_SIZE, k=cls.key("5")),
                sg.Button("6", s=INPUT_BUTTON_SIZE, k=cls.key("6")),
                sg.Button("/", s=INPUT_BUTTON_SIZE, k=cls.key("/")),
            ],
            [
                sg.Button("7", s=INPUT_BUTTON_SIZE, k=cls.key("7")),
                sg.Button("8", s=INPUT_BUTTON_SIZE, k=cls.key("8")),
                sg.Button("9", s=INPUT_BUTTON_SIZE, k=cls.key("9")),
                sg.Button("AC", key=cls.key("clear"), s=INPUT_BUTTON_SIZE),
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
                sg.Text("Registration Number:  "),
                sg.Input(
                    size=(25, 1),
                    justification="left",
                    key=cls.key("reg_num_input"),
                    focus=True,
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Column(column1, key=cls.key("column1")), sg.Push()],
            [sg.VPush()],
            cls.navigation_pane(),
        ]
        scrolled_layout = [
            [
                sg.Column(
                    layout,
                    scrollable=True,
                    vertical_scroll_only=True,
                    key=cls.key("main_column"),
                    expand_y=True,
                )
            ]
        ]
        return scrolled_layout

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        cls.adjust_input_field_size(window, ("reg_num_input", "column1"))
        window.refresh()

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == cls.key("back"):
            cls.back_nav_key_handler()
            return True
        if event == cls.key("home"):
            window_dispatch.dispatch.open_window("HomeWindow")
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
            cls.key("/"),
        ):
            keys_pressed = values[cls.key("reg_num_input")]
            keys_pressed += event.strip(cls.key_prefix())
            window[cls.key("reg_num_input")].update(keys_pressed)
            return True

        elif event == cls.key("clear"):
            window[cls.key("reg_num_input")].update("")
            cls.hide_message_display_field(window)
            cls.resize_column(window)
            return True

        elif event in (cls.key("submit"), cls.key("next")):
            if cls.validate(values, window) is not None:
                cls.resize_column(window)
                return True

            reg_number_entered = values[cls.key("reg_num_input")]

            student = Student.objects.filter(reg_number=reg_number_entered)
            if not student.exists():
                cls.popup_auto_close_error(
                    "No student found with given registration number."
                )
                return True
            cls.process_student(student, window)
        return True

    @classmethod
    def process_student(cls, student: Student, window: sg.Window) -> None:
        """Process staff info for update."""
        app_config.cp["tmp_student"] = app_config.cp.dict_vals_to_str(
            student.values(
                "reg_number",
                "first_name",
                "last_name",
                "level_of_study",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )

        tmp_student = app_config.cp["tmp_student"]
        if AttendanceRecord.objects.filter(
            attendance_session_id=app_config.cp.get(
                "current_attendance_session", "session_id"
            ),
            student_id=tmp_student["reg_number"],
        ).exists():
            cls.display_message("Student already signed in!", window)
            return
        cls.student_verification_window()

    @classmethod
    def validate(
        cls, values: Dict[str, Any], window: sg.Window
    ) -> Optional[bool]:
        """Validate values supplied by user in the window input fields."""
        for val_check in (
            cls.validate_required_field(
                (values[cls.key("reg_num_input")], "registration number")
            ),
            cls.validate_student_reg_number(values[cls.key("reg_num_input")]),
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

    @staticmethod
    def back_nav_key_handler() -> None:
        """Handle user pressing back button in nav pane."""
        window_dispatch.dispatch.open_window("AttendanceSessionLandingWindow")
        return
