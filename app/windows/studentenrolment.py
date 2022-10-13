import time
import json
from typing import Any, Dict, List, Optional

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.windows.basefingerprintverfication import FingerprintEnrolmentWindow
from app.windows.studentregnuminput import StudentRegNumInputWindow
from app.gui_utils import ValidationMixin
from app.nodedevicedatasynch import NodeDataSynch
import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from app.windows.basecamera import FaceCameraWindow
from db.models import Student, SexChoices, Faculty, Department, face_enc_to_str


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


def sync_student_data() -> None:
    """Synch student data to the server."""
    try:
        message = NodeDataSynch.student_register(
            app_config.cp.section_dict("new_student")
        )
    except Exception as e:
        error = json.loads(str(e))["detail"]
        BaseGUIWindow.popup_auto_close_error(error, duration=5)
    else:
        BaseGUIWindow.popup_auto_close_success(message, duration=5)

    app_config.cp.remove_section("new_student")
    return


class StudentEnrolmentWindow(ValidationMixin, BaseGUIWindow):
    """The GUI window for enrolment of student biodata."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        field_label_props = {"size": 22}
        combo_props = {"size": 22}
        input_props = {"size": 23}
        column1 = [
            [sg.Push(), sg.Text("Student Enrolment"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Registration Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_reg_number_input",
                    focus=True,
                    **input_props,
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_first_name",
                    **input_props,
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_last_name",
                    **input_props,
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_other_names",
                    **input_props,
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=cls.COMBO_DEFAULT,
                    key="student_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Level of study:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_level_of_study",
                    **input_props,
                ),
            ],
            [
                sg.Text("Possible graduation year:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_possible_grad_yr",
                    **input_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="student_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="student_department",
                    **combo_props,
                ),
            ],
        ]

        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
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
                    key="main_column",
                )
            ]
        ]
        window = sg.Window(
            "Student Enrolment", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == "student_faculty":
            if values["student_faculty"] in (cls.COMBO_DEFAULT, None):
                window["student_faculty"].update(
                    values=Faculty.get_all_faculties(), value=cls.COMBO_DEFAULT
                )
            else:
                window["student_department"].update(
                    values=Department.get_departments(
                        faculty=values["student_faculty"]
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == "submit":
            if cls.validate(values, window) is not None:
                window.refresh()
                window["main_column"].contents_changed()
                return True

            app_config.cp["new_student"] = {}
            app_config.cp["new_student"] = {
                "reg_number": values["student_reg_number_input"],
                "first_name": values["student_first_name"],
                "last_name": values["student_last_name"],
                "other_names": values["student_other_names"],
                "level_of_study": values["student_level_of_study"],
                "possible_grad_yr": values["student_possible_grad_yr"],
                "sex": SexChoices.str_to_value(values["student_sex"]),
                "department": Department.get_id(values["student_department"]),
            }
            new_student_dict = app_config.cp.section_dict("new_student")

            if (
                cls.__name__ == "StudentEnrolmentWindow"
                and Student.objects.filter(
                    reg_number=new_student_dict["reg_number"]
                ).exists()
            ):
                cls.display_message("Student profile already created!", window)
                return True

            if not OperationalMode.check_camera():
                cls.popup_auto_close_error("Camera not connected")
                time.sleep(1)
                if not OperationalMode.check_fingerprint():
                    cls.popup_auto_close_error(
                        "Fingerprint scanner not connected"
                    )
                    sync_student_data()
                    BaseGUIWindow.popup_auto_close_success(
                        "Student enrolment successful"
                    )
                    window_dispatch.dispatch.open_window("HomeWindow")
                    return True
                else:
                    window_dispatch.dispatch.open_window(
                        "StudentFingerprintEnrolmentWindow"
                    )
                    return True
            else:
                window_dispatch.dispatch.open_window(
                    "StudentFaceEnrolmentWindow"
                )
                return True
        if event == "cancel":
            window_dispatch.dispatch.open_window("HomeWindow")
        return True

    @classmethod
    def validate(
        cls, values: Dict[str, Any], window: sg.Window
    ) -> Optional[bool]:
        """Validate values supplied by user in the window input fields."""
        req_fields = [
            (values["student_reg_number_input"], "registration number"),
            (values["student_first_name"], "first name"),
            (values["student_last_name"], "last name"),
            (values["student_sex"], "sex"),
            (values["student_level_of_study"], "level of study"),
            (values["student_possible_grad_yr"], "possible year of graduation"),
            (values["student_faculty"], "faculty"),
            (values["student_department"], "department"),
        ]
        if cls.validate_required_fields(req_fields, window) is not None:
            return True

        for field in req_fields[1:3]:
            validation_val = cls.validate_text_field(*field)
            if validation_val is not None:
                cls.display_message(validation_val, window)
                return True

        for criteria in (
            cls.validate_student_reg_number(values["student_reg_number_input"]),
            cls.validate_sex(values["student_sex"]),
            cls.validate_faculty(values["student_faculty"]),
            cls.validate_department(values["student_department"]),
            cls.validate_int_field(
                values["student_level_of_study"], "level of study"
            ),
            cls.validate_int_field(
                values["student_possible_grad_yr"],
                "possible year of graduation",
            ),
        ):
            if criteria is not None:
                cls.display_message(criteria, window)
                return True
        return None


class StudentFaceEnrolmentWindow(FaceCameraWindow):
    """This window is used to capture face encodings for a new student
    being enrolled."""

    @classmethod
    def process_image(
        cls, captured_face_encodings: Any, window: sg.Window
    ) -> None:
        """Process detected face."""
        if captured_face_encodings is None:
            cls.popup_auto_close_error(
                "Error. Image must have exactly one face"
            )
            return
        app_config.cp["new_student"]["face_encodings"] = face_enc_to_str(
            captured_face_encodings
        )

        if not OperationalMode.check_fingerprint():
            BaseGUIWindow.popup_auto_close_warn(
                "Fingerprint scanner not available"
            )

            # save student if fingerprint enrolment not available
            sync_student_data()
            BaseGUIWindow.popup_auto_close_success(
                "Student enrolment successful"
            )

            window_dispatch.dispatch.open_window("StudentEnrolmentWindow")
            return

        window_dispatch.dispatch.open_window(
            "StudentFingerprintEnrolmentWindow"
        )
        return

    @staticmethod
    def cancel_camera() -> None:
        """ "Logic for when cancel button is pressed in camera window."""
        confirm = sg.popup_yes_no(
            "Student details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.cp.remove_section("new_student")
            window_dispatch.dispatch.open_window("HomeWindow")
        return


class StudentFingerprintEnrolmentWindow(FingerprintEnrolmentWindow):
    """This class provides methods tailored to student fingerprint enrolment."""

    @classmethod
    def process_fingerprint(cls, fingerprint_data: List[int]) -> None:
        """Process captured fingerprint template."""
        app_config.cp["new_student"]["fingerprint_template"] = str(
            fingerprint_data
        )
        sync_student_data()
        cls.popup_auto_close_success("Student enrolment successful")
        window_dispatch.dispatch.open_window("StudentEnrolmentWindow")
        return

    @staticmethod
    def cancel_fp_enrolment() -> None:
        """Next window when user presses cancel button on GUI window."""
        confirm = sg.popup_yes_no(
            "Student details will be saved with no fingerprint biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.cp.remove_section("new_student")
            window_dispatch.dispatch.open_window("HomeWindow")
        return

    @classmethod
    def window_title(cls) -> str:
        """Title of the GUI window."""
        return "Student Fingerprint Enrolment"


class StudentEnrolmentUpdateWindow(StudentEnrolmentWindow):
    """A window for updating biodata of existing student."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        student = app_config.cp["new_student"]

        try:
            student_sex = SexChoices(int(student["sex"])).label
        except Exception:
            student_sex = None

        field_label_props = {"size": 22}
        combo_props = {"size": 22}
        input_props = {"size": 23}
        column1 = [
            [sg.Push(), sg.Text("Student Enrolment"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Registration Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_reg_number_input",
                    disabled=True,
                    **input_props,
                    default_text=student["reg_number"],
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_first_name",
                    focus=True,
                    **input_props,
                    default_text=student["first_name"],
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_last_name",
                    **input_props,
                    default_text=student["last_name"],
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_other_names",
                    **input_props,
                    default_text=student["other_names"],
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=student_sex or cls.COMBO_DEFAULT,
                    key="student_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Level of study:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_level_of_study",
                    **input_props,
                    default_text=student["level_of_study"],
                ),
            ],
            [
                sg.Text("Possible graduation year:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_possible_grad_yr",
                    **input_props,
                    default_text=student["possible_grad_yr"],
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=student["department__faculty__name"],
                    enable_events=True,
                    key="student_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=student["department__name"],
                    enable_events=True,
                    key="student_department",
                    **combo_props,
                ),
            ],
        ]

        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
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
                    key="main_column",
                )
            ]
        ]
        window = sg.Window(
            "Student Enrolment", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        return super().loop(window, event, values)


class StudentEnrolmentUpdateIDSearch(StudentRegNumInputWindow):
    """Window for finding student by reg number for bio data update."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        return super().window()

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        return super().loop(window, event, values)

    @classmethod
    def process_student(cls, student: Student) -> None:
        """Process staff info for update."""
        app_config.cp["new_student"] = app_config.cp.dict_vals_to_str(
            student.values(
                "reg_number",
                "first_name",
                "last_name",
                "other_names",
                "level_of_study",
                "possible_grad_yr",
                "sex",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )
        window_dispatch.dispatch.open_window("StudentEnrolmentUpdateWindow")
        return
