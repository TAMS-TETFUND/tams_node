import time
from typing import Any, Dict, Iterable

import PySimpleGUI as sg

import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from db.models import SexChoices, Faculty, Department
from .staffenrolmentwin import StaffEnrolmentWindow
from .utils import send_staff_data

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffEnrolmentUpdateWindow(StaffEnrolmentWindow):
    """A window for updating biodata of existing staff."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        staff = app_config.cp["edit_staff"]

        try:
            staff_sex = SexChoices(int(staff["sex"])).label
        except Exception:
            staff_sex = None

        field_label_props = {"size": 16}
        combo_props = {"size": 25}
        input_props = {"size": 26}
        column1 = [
            [sg.Push(), sg.Text("Staff Enrolment Update"), sg.Push()],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Staff Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("staff_number_input"),
                    disabled=True,
                    **input_props,
                    default_text=staff["staff_number"],
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    focus=True,
                    key=cls.key("staff_first_name"),
                    **input_props,
                    default_text=staff["first_name"],
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    default_text=staff["last_name"],
                    key=cls.key("staff_last_name"),
                    **input_props,
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    default_text=staff["other_names"],
                    key=cls.key("staff_other_names"),
                    **input_props,
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=staff_sex or cls.COMBO_DEFAULT,
                    key=cls.key("staff_sex"),
                    **combo_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=staff["department__faculty__name"],
                    enable_events=True,
                    key=cls.key("staff_faculty"),
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=staff["department__name"],
                    enable_events=True,
                    key=cls.key("staff_department"),
                    **combo_props,
                ),
            ],
        ]
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1, pad=(0, None)),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key=cls.key("submit")),
                sg.Button("Cancel", key=cls.key("cancel"), **cls.cancel_button_kwargs()),
            ],
            [sg.VPush()],
        ]

        scrolled_layout = [
            [
                sg.Column(
                    layout,
                    scrollable=True,
                    vertical_scroll_only=True,
                    expand_y=True,
                    expand_x=True,
                    pad=(0, 0),
                    key=cls.key("main_column"),
                )
            ]
        ]
        return scrolled_layout

    @classmethod
    def adjust_input_field_size(cls, window: sg.Window, input_fields: Iterable[str] = ("staff_number_input", "staff_first_name", "staff_last_name", "staff_other_names", "staff_sex", "staff_faculty", "staff_department",)) -> None:
        """Adjust input field sizes to avoid uneven widths in appearance."""
         
        for key in input_fields:
            window[cls.key(key)].expand(expand_x=True)

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any],
    ) -> bool:
        """Track user interaction with window."""
        return super().loop(window, event, values)

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        cls.adjust_input_field_size(window, ("staff_number_input", "staff_first_name", "staff_last_name", "staff_other_names", "staff_sex", "staff_faculty", "staff_department",))
        staff = app_config.cp["edit_staff"]
        try:
            staff_sex = SexChoices(int(staff["sex"])).label
        except Exception:
            staff_sex = None
        window[cls.key("staff_number_input")].update(staff.get("staff_number", fallback=""))
        window[cls.key("staff_first_name")].update(staff.get("first_name", fallback=""))
        window[cls.key("staff_last_name")].update(staff.get("last_name", fallback=""))
        window[cls.key("staff_other_names")].update(staff.get("other_names", fallback=""))
        window[cls.key("staff_sex")].update(staff_sex)
        window[cls.key("staff_faculty")].update(staff.get("department__faculty__name", fallback=""))
        window[cls.key("staff_department")].update(staff.get("department", fallback=""))

    @classmethod
    def next_window(cls) -> None:
        """Open next window when processing of submitted data is complete."""
        change_password = sg.popup_yes_no("Do you want to change password?", keep_on_top=True)
        if change_password == "Yes":
            window_dispatch.dispatch.open_window("StaffPasswordSettingUpdateWindow")
            return
        
        if not OperationalMode.check_camera():
            cls.popup_auto_close_warn("Camera not connected.", keep_on_top=True)
            time.sleep(2)
            if not OperationalMode.check_fingerprint():
                cls.popup_auto_close_warn("Fingerprint scanner not connected")
                window_dispatch.dispatch.open_window("HomeWindow")
            else:
                update_fingerprint = sg.popup_yes_no("Update fingerprint?", keep_on_top=True)
                if update_fingerprint == "Yes":
                    window_dispatch.dispatch.open_window(
                        "StaffFingerprintEnrolmentWindow"
                    )
                    return
        else:
            update_face = sg.popup_yes_no("Update face capture?", keep_on_top=True)
            if update_face == "Yes":
                window_dispatch.dispatch.open_window("StaffFaceEnrolmentUpdateWindow")
                return
        send_staff_data()
        window_dispatch.dispatch.open_window("HomeWindow")
        return