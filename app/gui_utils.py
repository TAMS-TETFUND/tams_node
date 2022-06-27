import app
from app.opmodes import OpModes
from db.models import Student, Semester, AcademicSession, Staff, Faculty, Department, Sex

class StaffBiometricVerificationRouterMixin:
    @classmethod
    def staff_verification_window(cls):
        tmp_staff = app.gui.app_config["tmp_staff"]
        device_op_mode = app.gui.app_config.getint("tmp_settings", "op_mode")
        if device_op_mode == OpModes.FINGERPRINT.value:
            if tmp_staff["fingerprint_template"] in (None, "None", ""):
                cls.popup_auto_close_error("No fingerprint registration data found")
            else:
                app.gui.window_dispatch.open_window(app.gui.StaffFingerprintVerificationWindow)
            return
        if device_op_mode == OpModes.FACE.value:
            if tmp_staff["face_encodings"] in (None, "None", ""):
                cls.popup_auto_close_error("No facial registration data found")
            else:
                app.gui.window_dispatch.open_window(app.gui.StaffFaceVerificationWindow)
            return
        if device_op_mode == OpModes.BIMODAL.value:
            if tmp_staff["fingerprint_template"] in (None, "None", ""):
                if tmp_staff["face_encodings"] in (None, "None", ""):
                    cls.popup_auto_close_error("No biometric data found for staff")
                    return
                else:
                    app.gui.window_dispatch.open_window(app.gui.StaffFaceVerificationWindow)
                    return
            else:
                app.gui.window_dispatch.open_window(app.gui.StaffFingerprintVerificationWindow)
                return


class StaffIDInputRouterMixin:
    """Mixin to hadle routing of user to window for staff id input.
    Routing will depend on presence/absence of camera module in device."""
    @staticmethod
    def staff_id_input_window():
        if app.gui.app_config.getint("tmp_settings", "op_mode") in (OpModes.FACE.value, OpModes.BIMODAL.value):
            app.gui.window_dispatch.open_window(app.gui.StaffBarcodeCameraWindow)
        else:
            app.gui.window_dispatch.open_window(app.gui.StaffNumberInputWindow)
        return


class StudentBiometricVerificationRouterMixin:
    """Mixin for routing student verification to appropriate window."""
    @classmethod
    def student_verification_window(cls):
        tmp_student = app.gui.app_config["tmp_student"]
        device_op_mode = app.gui.app_config.getint("tmp_settings", "op_mode")
        if device_op_mode == OpModes.FINGERPRINT.value:
            if tmp_student["fingerprint_template"] in (None, "None", ""):
                cls.popup_auto_close_error("No fingerprint registration data found")
            else:
                app.gui.window_dispatch.open_window(app.gui.StudentFingerprintVerificationWindow)
            return
        if device_op_mode == OpModes.FACE.value:
            if tmp_student["face_encodings"] in (None, "None", ""):
                cls.popup_auto_close_error("No facial registration data found")
            else:
                app.gui.window_dispatch.open_window(app.gui.StaffFaceVerificationWindow)
            return
        if device_op_mode == OpModes.BIMODAL.value:
            if tmp_student["fingerprint_template"] in (None, "None", ""):
                if tmp_student["face_encodings"] in (None, "None", ""):
                    cls.popup_auto_close_error("No biometric data found for student")
                    return
                else:
                    app.gui.window_dispatch.open_window(app.gui.StudentFaceVerificationWindow)
                    return
            else:
                app.gui.window_dispatch.open_window(app.gui.StudentFingerprintVerificationWindow)
                return


class StudentRegNumberInputRouterMixin:
    """Mixin to handle routing of student to window for student 
    reg number input. Routing will depend on presence/absence of camera module in device"""
    @staticmethod
    def student_reg_number_input_window():
        if app.gui.app_config.getint("tmp_settings", "op_mode") in (OpModes.FACE.value, OpModes.BIMODAL.value):
            app.gui.window_dispatch.open_window(app.gui.StudentBarcodeCameraWindow)
        else:
            app.gui.window_dispatch.open_window(app.gui.StudentRegNumInputWindow)
        return


class ValidationMixin:
    """Mixin to handle input field validations."""

    @staticmethod
    def validate_required_field(req_field):
        field_value, field_name_for_display = req_field
        if field_value in (None, "", "--select--"):
            return "Invalid value provided in {}".format(field_name_for_display)
        else:
            return None

    @classmethod
    def validate_required_fields(cls, req_fields, window):
        for field in req_fields:
            validation_value = cls.validate_required_field(field)
            if validation_value is not None:
                cls.display_message(validation_value, window)
                return True
            else:
                return None

    @staticmethod
    def validate_semester(semester):
        if semester not in Semester.labels:
            return "Invalid value for semester"
        else:
            return None

    @staticmethod
    def validate_academic_session(session):
        if not AcademicSession.is_valid_session(session):
            return "Invalid value for academic session"
        else:
            return None

    @staticmethod
    def validate_student_reg_number(reg_no):
        if not Student.is_valid_student_reg_number(reg_no):
            return f"Invalid format for student registration number ({reg_no})"
        else:
            return None

    @staticmethod
    def validate_staff_number(staff_no):
        if not Staff.is_valid_staff_number(staff_no):
            return "Invalid value for staff number"
        else:
            return None

    @staticmethod
    def validate_faculty(faculty):
        if faculty.lower() not in [
            fac.lower() for fac in Faculty.get_all_faculties()
        ]:
            return "Invalid value in faculty"
        else:
            return None

    @staticmethod
    def validate_department(department):
        if department.lower() not in [
            dept.lower() for dept in Department.get_departments()
        ]:
            return "Invalid value in department"
        else:
            return None

    @staticmethod
    def validate_sex(sex):
        if sex not in Sex.labels:
            return "Invalid value in sex"
        else:
            return None

    @staticmethod
    def validate_int_field(field_value, field_name):
        try:
            field_val_int = int(field_value)
        except Exception:
            return f"Enter a numeric value for {field_name}"
        else:
            return None

    @staticmethod
    def validate_text_field(field_value, field_name):
        if len(field_value) == 0:
            return f"{field_name.capitalize()} cannot be blank"
        else:
            return None
