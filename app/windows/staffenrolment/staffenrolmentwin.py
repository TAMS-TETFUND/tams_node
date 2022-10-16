import json
from typing import Any, Dict, Optional

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.guiutils import ValidationMixin
import app.appconfigparser
import app.windowdispatch
from db.models import Staff, SexChoices, Faculty, Department

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffEnrolmentWindow(ValidationMixin, BaseGUIWindow):
    """The GUI window for enrolment of staff biodata"""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        field_label_props = {"size": 16}
        combo_props = {"size": 25}
        input_props = {"size": 26}
        column1 = [
            [sg.Push(), sg.Text("Staff Enrolment"), sg.Push()],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Staff Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("staff_number_input"),
                    focus=True,
                    **input_props,
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left", key=cls.key("staff_first_name"), **input_props
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left", key=cls.key("staff_last_name"), **input_props
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left", key=cls.key("staff_other_names"), **input_props
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=cls.COMBO_DEFAULT,
                    key=cls.key("staff_sex"),
                    **combo_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key=cls.key("staff_faculty"),
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
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
        # for key in (
        #     "staff_number_input",
        #     "staff_first_name",
        #     "staff_last_name",
        #     "staff_other_names",
        #     "staff_sex",
        #     "staff_faculty",
        #     "staff_department",
        # ):
        #     window[key].expand(expand_x=True)
        return scrolled_layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == cls.key("staff_faculty"):
            if values[cls.key("staff_faculty")] in (cls.COMBO_DEFAULT, None):
                window[cls.key("staff_faculty")].update(
                    values=Faculty.get_all_faculties(), value=cls.COMBO_DEFAULT
                )
            else:
                window[cls.key("staff_department")].update(
                    values=Department.get_departments(
                        faculty=values[cls.key("staff_faculty")]
                    ),
                    value=cls.COMBO_DEFAULT,
                )

        if event == cls.key("submit"):
            if cls.validate(values, window) is not None:
                window.refresh()
                window[cls.key("main_column")].contents_changed()
                return True

            values[cls.key("staff_number_input")] = values[cls.key("staff_number_input")].upper()

            app_config.cp["new_staff"] = {
                "username": values[cls.key("staff_number_input")],
                "staff_number": values[cls.key("staff_number_input")],
                "first_name": values[cls.key("staff_first_name")],
                "last_name": values[cls.key("staff_last_name")],
                "other_names": values[cls.key("staff_other_names")],
                "department": Department.get_id(values[cls.key("staff_department")]),
                "sex": SexChoices.str_to_value(values[cls.key("staff_sex")]),
            }
            new_staff_dict = app_config.cp.section_dict("new_staff")

            if (
                cls.__name__ == "StaffEnrolmentWindow"
                and Staff.objects.filter(
                    staff_number=new_staff_dict["staff_number"]
                ).exists()
            ):
                cls.display_message("Staff profile already created!", window)
                return True
            
            cls.next_window()
        if event == cls.key("cancel"):
            window_dispatch.dispatch.open_window("HomeWindow")

        return True

    @classmethod
    def validate(
        cls, values: Dict[str, Any], window: sg.Window
    ) -> Optional[bool]:
        """Validate values supplied by user in the window input fields."""
        req_fields = [
            (values[cls.key("staff_number_input")], "staff number"),
            (values[cls.key("staff_first_name")], "first name"),
            (values[cls.key("staff_last_name")], "last name"),
            (values[cls.key("staff_sex")], "sex"),
            (values[cls.key("staff_faculty")], "faculty"),
            (values[cls.key("staff_department")], "department"),
        ]
        validation_val = cls.validate_required_fields(req_fields, window)
        if validation_val is not None:
            return True

        for field in req_fields[1:3]:
            validation_val = cls.validate_text_field(*field)
            if validation_val is not None:
                cls.display_message(validation_val, window)
                return True

        for criteria in (
            cls.validate_staff_number(values[cls.key("staff_number_input")]),
            cls.validate_sex(values[cls.key("staff_sex")]),
            cls.validate_faculty(values[cls.key("staff_faculty")]),
            cls.validate_department(values[cls.key("staff_department")]),
        ):
            if criteria is not None:
                cls.display_message(criteria, window)
                return True
        return None

    @classmethod
    def next_window(cls) -> None:
        """Open next window when processing of submitted data is complete."""
        window_dispatch.dispatch.open_window("StaffPasswordSettingWindow")


    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        cls.adjust_input_field_size(window, ("staff_number_input", "staff_first_name", "staff_last_name", "staff_other_names", "staff_sex", "staff_faculty", "staff_department",))