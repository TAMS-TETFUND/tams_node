import json
import time

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.windows.basefingerprintverfication import FingerprintEnrolmentWindow
from app.windows.staffnumberinput import StaffNumberInputWindow
from app.gui_utils import ValidationMixin
from app.nodedevicedatasynch import NodeDataSynch
import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from app.windows.basecamera import FaceCameraWindow
from db.models import Staff, SexChoices, Faculty, Department, face_enc_to_str

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()

class StaffEnrolmentWindow(ValidationMixin, BaseGUIWindow):
    """The GUI window for enrolment of staff biodata"""

    @classmethod
    def window(cls):
        # cls.enroll_update = True
        field_label_props = {"size": 16}
        combo_props = {"size": 28}
        input_props = {"size": 29}
        column1 = [
            [sg.Push(), sg.Text("Staff Enrolment"), sg.Push()],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Staff Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="staff_number_input",
                    focus=True,
                    **input_props,
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left", key="staff_first_name", **input_props
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left", key="staff_last_name", **input_props
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left", key="staff_other_names", **input_props
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=cls.COMBO_DEFAULT,
                    key="staff_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="staff_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="staff_department",
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
            "Staff Enrolment", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "staff_faculty":
            if values["staff_faculty"] in (cls.COMBO_DEFAULT, None):
                window["staff_faculty"].update(
                    values=Faculty.get_all_faculties(), value=cls.COMBO_DEFAULT
                )
            else:
                window["staff_department"].update(
                    values=Department.get_departments(
                        faculty=values["staff_faculty"]
                    ),
                    value=cls.COMBO_DEFAULT,
                )

        if event == "submit":
            if cls.validate(values, window) is not None:
                window.refresh()
                window["main_column"].contents_changed()
                return True

            values["staff_number_input"] = values["staff_number_input"].upper()

            app_config.cp["new_staff"] = {
                "username": values["staff_number_input"],
                "staff_number": values["staff_number_input"],
                "first_name": values["staff_first_name"],
                "last_name": values["staff_last_name"],
                "other_names": values["staff_other_names"],
                "department": Department.get_id(values["staff_department"]),
                "sex": SexChoices.str_to_value(values["staff_sex"]),
            }

            new_staff_dict = app_config.cp.section_dict("new_staff")

            if cls.__name__ == "StaffEnrolmentWindow" and Staff.objects.filter(
                    staff_number=new_staff_dict["staff_number"]
            ).exists():
                cls.display_message("Staff already exist!", window)
                return True
            # else:
            #     Staff.objects.create_user(
            #         department=department, **new_staff_dict
            #     )

            cls.next_window()
        if event == "cancel":
            window_dispatch.dispatch.open_window("HomeWindow")

        return True

    @classmethod
    def validate(cls, values, window):
        req_fields = [
            (values["staff_number_input"], "staff number"),
            (values["staff_first_name"], "first name"),
            (values["staff_last_name"], "last name"),
            (values["staff_sex"], "sex"),
            (values["staff_faculty"], "faculty"),
            (values["staff_department"], "department"),
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
                cls.validate_staff_number(values["staff_number_input"]),
                cls.validate_sex(values["staff_sex"]),
                cls.validate_faculty(values["staff_faculty"]),
                cls.validate_department(values["staff_department"]),
        ):
            if criteria is not None:
                cls.display_message(criteria, window)
                return True
        return None

    @classmethod
    def next_window(cls):
        window_dispatch.dispatch.open_window("StaffPasswordSettingWindow")


class StaffPasswordSettingWindow(BaseGUIWindow):
    """This window is used for setting password for the new staff being
    enrolled."""

    @classmethod
    def window(cls):
        field_label_props = {"size": 25}
        layout = [
            [sg.Text("Set Password")],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Password:", **field_label_props),
                sg.Input(
                    key="staff_password",
                    expand_x=True,
                    enable_events=True,
                    password_char="*",
                    focus=True,
                ),
            ],
            [
                sg.Text("Confirm Password:", **field_label_props),
                sg.Input(
                    key="staff_password_confirm",
                    expand_x=True,
                    password_char="*",
                ),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
            ],
            cls.navigation_pane(
                next_icon="next_disabled", back_icon="back_disabled"
            ),
        ]
        window = sg.Window(
            "Staff Password Setup", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("staff_password", "staff_password_confirm"):
            if values["staff_password"] != values["staff_password_confirm"]:
                cls.display_message(
                    "Re-enter the same password in the 'Confirm Password' field",
                    window,
                )
            else:
                cls.display_message("", window)

        if event in ("cancel", "submit"):
            new_staff = app_config.cp["new_staff"]

            if event == "submit":
                # todo: verify that password is the same on submit
                password_fields = (
                    values["staff_password"],
                    values["staff_password_confirm"],
                )
                for field in password_fields:
                    if field in (None, ""):
                        cls.display_message(
                            "Enter password and confirmation", window
                        )
                        return True

                new_staff["password"] = values["staff_password"]

                if not OperationalMode.check_camera():
                    cls.popup_auto_close_warn("Camera not connected.")
                    time.sleep(2)
                    if not OperationalMode.check_fingerprint():
                        cls.popup_auto_close_warn(
                            "Fingerprint scanner not connected"
                        )
                        window_dispatch.dispatch.open_window("HomeWindow")
                    else:
                        window_dispatch.dispatch.open_window(
                            "StaffFingerprintEnrolmentWindow"
                        )
                else:
                    window_dispatch.dispatch.open_window("StaffFaceEnrolmentWindow")
                return True

            if event in ("cancel", "home"):
                confirm = sg.popup_yes_no(
                    "Cancel Staff registration?",
                    title="Cancel Registration",
                    keep_on_top=True,
                )
                if confirm == "Yes":
                    # todo: clear app config section 'new staff'
                    window_dispatch.dispatch.open_window("StaffEnrolmentWindow")
                    return True
                else:
                    return True
        return True


class StaffFaceEnrolmentWindow(FaceCameraWindow):
    """This window is used to capture face encodings for a new staff
    being enrolled."""

    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.popup_auto_close_error(
                "Error. Image must have exactly one face"
            )
            return
        new_staff = app_config.cp["new_staff"]

        # try:
        #     staff = Staff.objects.get(staff_number=new_staff["staff_number"])
        # except Exception as e:
        #     cls.popup_auto_close_error(e)
        #     return

        new_staff["face_encodings"] = face_enc_to_str(captured_face_encodings)

        window_dispatch.dispatch.open_window("StaffFingerprintEnrolmentWindow")
        cls.popup_auto_close_success("Biometric data saved")
        return

    @staticmethod
    def cancel_camera():
        confirm = sg.popup_yes_no(
            "Staff details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.cp.remove_section("new_staff")
            window_dispatch.dispatch.open_window("HomeWindow")
        return


class StaffFingerprintEnrolmentWindow(FingerprintEnrolmentWindow):
    """This class provides methods tailored to staff fingerprint enrolement."""

    @classmethod
    def process_fingerprint(cls, fingerprint_data):
        app_config.cp["new_staff"]['fingerprint_template'] = str(fingerprint_data)
        cls.post_process_enrolment_config()
        cls.popup_auto_close_success("Staff enrolment successful")
        window_dispatch.dispatch.open_window("StaffEnrolmentWindow")
        return

    @staticmethod
    def cancel_fp_enrolment():
        confirm = sg.popup_yes_no(
            "Staff details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.cp.remove_section("new_staff")
            window_dispatch.dispatch.open_window("HomeWindow")
        return

    @staticmethod
    def post_process_enrolment_config():
        try:
            message = NodeDataSynch.staff_register(
                app_config.cp.section_dict("new_staff")
            )
            BaseGUIWindow.popup_auto_close_success(message, duration=5)
            app_config.cp.remove_section("new_staff")
            # sync server data with the node device

        except Exception as e:
            error = json.loads(str(e))["detail"]
            BaseGUIWindow.popup_auto_close_error(error, duration=5)

        app_config.cp.remove_section("new_staff")
        return

    @classmethod
    def window_title(cls):
        return "Student Fingerprint Verification"


class StaffEnrolmentUpdateIDSearch(StaffNumberInputWindow):
    @classmethod
    def window(cls):
        return super().window()

    @classmethod
    def loop(cls, window, event, values):
        return super().loop(window, event, values)

    @classmethod
    def process_staff(cls, staff):
        app_config.cp["edit_staff"] = app_config.cp.dict_vals_to_str(
            staff.values(
                "staff_number",
                "first_name",
                "last_name",
                "other_names",
                "sex",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )
        window_dispatch.dispatch.open_window("StaffEnrolmentUpdateWindow")
        return

    @staticmethod
    def back_nav_key_handler():
        window_dispatch.dispatch.open_window("HomeWindow")
        return


class StaffEnrolmentUpdateWindow(StaffEnrolmentWindow):
    """A window for updating biodata of existing staff."""
    enroll_update = "update"

    @classmethod
    def window(cls):
        # cls.enroll_update = False
        staff = app_config.cp["edit_staff"]

        try:
            staff_sex = SexChoices(int(staff["sex"])).label
        except Exception:
            staff_sex = None

        field_label_props = {"size": 16}
        combo_props = {"size": 28}
        input_props = {"size": 29}
        column1 = [
            [sg.Push(), sg.Text("Staff Enrolment"), sg.Push()],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Staff Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="staff_number_input",
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
                    key="staff_first_name",
                    **input_props,
                    default_text=staff["first_name"],
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    default_text=staff["last_name"],
                    key="staff_last_name",
                    **input_props,
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    default_text=staff["other_names"],
                    key="staff_other_names",
                    **input_props,
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=staff_sex or cls.COMBO_DEFAULT,
                    key="staff_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=staff["department__faculty__name"],
                    enable_events=True,
                    key="staff_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=staff["department__name"],
                    enable_events=True,
                    key="staff_department",
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
            "Staff Enrolment", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        return super().loop(window, event, values)

    @classmethod
    def next_window(cls):
        if not OperationalMode.check_camera():
            cls.popup_auto_close_warn("Camera not connected.")
            time.sleep(2)
            if not OperationalMode.check_fingerprint():
                cls.popup_auto_close_warn("Fingerprint scanner not connected")
                window_dispatch.dispatch.open_window("HomeWindow")
            else:
                window_dispatch.dispatch.open_window("StaffFingerprintEnrolmentWindow")
        else:
            window_dispatch.dispatch.open_window("StaffFaceEnrolmentWindow")