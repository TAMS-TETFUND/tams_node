from django.db.utils import IntegrityError

from app.appconfigparser import AppConfigParser
from db.models import AttendanceRecord


# initializing the configparser object
app_config = AppConfigParser()


class AttendanceLogger:
    tmp_student = app_config["tmp_student"]
    message = ""
    @classmethod
    def log_attendance(cls):
        try:
            AttendanceRecord.objects.create(
                attendance_session_id=app_config.getint(
                    "current_attendance_session", "session_id"
                ),
                student_id=cls.tmp_student.getint("id"),
            )
        except IntegrityError:
            cls.message = "Something went wrong. Please contact admin."
            return False
        else:
            cls.message = f"{cls.tmp_student['reg_number']} checked in"
            return True
    
    @classmethod
    def log_failed_attempts(cls):
        """This method will block a student after they attempt to 
        log attendance 4 times unsuccessfully.
        """
        if "failed_attempts" not in app_config:
            app_config["failed_attempts"] = {}
        
        student_reg_number = cls.tmp_student["reg_number"]
        failed_attempts = app_config["failed_attempts"]

        if student_reg_number not in failed_attempts:
            failed_attempts[student_reg_number] = str(1)

        elif failed_attempts.getint(student_reg_number) >= 3:
            if (
                "blocked_reg_numbers"
                not in app_config["current_attendance_session"]
            ):
                app_config["current_attendance_session"][
                    "blocked_reg_numbers"
                ] = ""
            app_config["current_attendance_session"][
                "blocked_reg_numbers"
            ] += ("," + student_reg_number)
        
        else:
            failed_attempts[student_reg_number] = str(failed_attempts.getint(student_reg_number) + 1)