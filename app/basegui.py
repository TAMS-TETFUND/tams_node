import io
import json
import os
from pathlib import Path
import base64

from PIL import Image
import PySimpleGUI as sg
from manage import init_django

init_django()

from db.models import Department, Faculty, Sex, Student, Staff


# set application-wide theme
sg.theme("LightGreen6")


class BaseGUIWindow:
    COMBO_DEFAULT = "--select--"
    SCREEN_SIZE = (480, 320)
    ICON_SIZE = {"h": 125, "w": 70}
    ICON_BUTTON_COLOR = (
        sg.theme_background_color(),
        sg.theme_background_color(),
    )

    @classmethod
    def window(cls):
        raise NotImplementedError

    @classmethod
    def loop(cls, window, event, values):
        raise NotImplementedError

    @staticmethod
    def _image_file_to_bytes(image64, size):
        image_file = io.BytesIO(base64.b64decode(image64))
        img = Image.open(image_file)
        img.thumbnail(size, Image.ANTIALIAS)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        imgbytes = bio.getvalue()
        return imgbytes

    @classmethod
    def get_icon(cls, icon_name, size_ratio=1):
        icons_path = os.path.join(
            Path(os.path.abspath(__file__)).parent, "icons.json"
        )
        with open(icons_path, "r") as data:
            icon_dict = json.loads(data.read())
        icon = icon_dict[icon_name]
        return cls._image_file_to_bytes(
            icon,
            (cls.ICON_SIZE["h"] * size_ratio, cls.ICON_SIZE["w"] * size_ratio),
        )

    @classmethod
    def window_init_dict(cls):
        init_dict = {
            "size": cls.SCREEN_SIZE,
            "no_titlebar": True,
            "keep_on_top": True,
            "grab_anywhere": True,
            "finalize": True,
            "use_custom_titlebar": False,
        }
        return init_dict

    @staticmethod
    def message_display():
        return sg.pin(
            sg.Text("", enable_events=True, k="message_display", visible=False)
        )

    @staticmethod
    def validate_required_field(field_value, field_name):
        if field_value in (None, "", "--select--"):
            return "Invalid value provided in {}".format(
                " ".join(field_name.split("_"))
            )
        return None

    @staticmethod
    def get_int(field_value):
        try:
            field_value_int = int(field_value)
        except ValueError:
            return None
        else:
            return field_value_int

    @staticmethod
    def validate_student_reg_number(reg_no):
        if not Student.is_valid_student_reg_number(reg_no):
            return "Invalid value for student registration number"
        return None

    @staticmethod
    def validate_staff_number(staff_no):
        if not Staff.is_valid_staff_number(staff_no):
            return "Invalid value for staff number"
        return None

    @staticmethod
    def validate_faculty(faculty):
        if faculty.lower() not in [
            fac.lower() for fac in Faculty.get_all_faculties()
        ]:
            return "Invalid value in faculty"
        return None

    @staticmethod
    def validate_department(department):
        if department.lower() not in [
            dept.lower() for dept in Department.get_departments()
        ]:
            return "Invalid value in department"
        return None

    @staticmethod
    def validate_sex(sex):
        if sex not in Sex.labels:
            return "Invalid value in sex"
        return None

    @staticmethod
    def validate_int_field(field_value, field_name):
        try:
            field_val_int = int(field_value)
        except Exception:
            return f"Enter a numeric value for {field_name}"
        else:
            return None
