import app
from app.opmodes import OpModes


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