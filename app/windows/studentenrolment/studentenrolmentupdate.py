from typing import Any, Dict, List

import PySimpleGUI as sg

import app.appconfigparser
import app.windowdispatch
from db.models import SexChoices, Faculty, Department
from .studentenrolmentwin import StudentEnrolmentWindow


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentEnrolmentUpdateWindow(StudentEnrolmentWindow):
    """A window for updating biodata of existing student."""
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        student = app_config.cp["new_student"]

        try:
            student_sex = SexChoices(int(student["sex"])).label
        except Exception:
            student_sex = None

        field_label_props = {"size": 22}
        combo_props = {"size": 20}
        input_props = {"size": 21}
        column1 = [
            [sg.Push(), sg.Text("Student Enrolment"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Registration Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("student_reg_number_input"),
                    disabled=True,
                    **input_props,
                    default_text=student.get("reg_number", fallback=""),
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("student_first_name"),
                    focus=True,
                    **input_props,
                    default_text=student.get("first_name", fallback=""),
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("student_last_name"),
                    **input_props,
                    default_text=student.get("last_name", fallback=""),
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("student_other_names"),
                    **input_props,
                    default_text=student.get("other_names", ""),
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=student_sex or cls.COMBO_DEFAULT,
                    key=cls.key("student_sex"),
                    **combo_props,
                ),
            ],
            [
                sg.Text("Level of study:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("student_level_of_study"),
                    **input_props,
                    default_text=student.get("level_of_study", fallback=""),
                ),
            ],
            [
                sg.Text("Possible graduation year:", **field_label_props),
                sg.Input(
                    justification="left",
                    key=cls.key("student_possible_grad_yr"),
                    **input_props,
                    default_text=student.get("possible_grad_yr", fallback=""),
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=student.get("department__faculty__name", fallback=""),
                    enable_events=True,
                    key=cls.key("student_faculty"),
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=student.get("department__name", fallback=""),
                    enable_events=True,
                    key=cls.key("student_department"),
                    **combo_props,
                ),
            ],
        ]

        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1, pad=(0, 0)),
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
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        return super().loop(window, event, values)

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        cls.adjust_input_field_size(window, [
            "student_reg_number_input", 
            "student_first_name", 
            "student_last_name", 
            "student_other_names", 
            "student_sex", 
            "student_level_of_study", 
            "student_possible_grad_yr", 
            "student_faculty",
            "student_department",]
        )
        student = app_config.cp["new_student"]
        try:
            student_sex = SexChoices(int(student["sex"])).label
        except Exception:
            student_sex = None

        window[cls.key("student_reg_number_input")].update(student.get("reg_number", fallback=""))
        window[cls.key("student_first_name")].update(student.get("first_name", fallback=""))
        window[cls.key("student_last_name")].update(student.get("last_name", fallback=""))
        window[cls.key("student_other_names")].update(student.get("other_names", fallback=""))
        window[cls.key("student_sex")].update(student_sex or cls.COMBO_DEFAULT)
        window[cls.key("student_level_of_study")].update(student.get("level_of_study", fallback=""))
        window[cls.key("student_possible_grad_yr")].update(student.get("possible_grad_yr", fallback=""))
        window[cls.key("student_faculty")].update(student.get("department__faculty__name", fallback=""))
        window[cls.key("student_department")].update(student.get("department__name", fallback=""))