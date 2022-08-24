from django.db.utils import IntegrityError
from django.utils import timezone

from app.appconfigparser import AppConfigParser
from db.models import AttendanceRecord, RecordTypesChoices


class AttendanceLogger:
    message = ""

    @classmethod
    def log_attendance(cls, app_config: AppConfigParser):
        """This method handles student attendance logging.
        Returns True if attendance logging is successful
        False if attendance logging is unsuccessful
        """
        tmp_student = app_config["tmp_student"]
        try:
            obj, created = AttendanceRecord.objects.update_or_create(
                attendance_session_id=app_config.get(
                    "current_attendance_session", "session_id"
                ),
                student_id=tmp_student["reg_number"],
                defaults={"record_type": RecordTypesChoices.SIGN_IN},
            )
        except IntegrityError:
            cls.message = "Something went wrong. Please contact admin."
            return False
        else:
            if created:
                cls.message = f"{tmp_student['reg_number']} checked in"
            else:
                obj.record_type = RecordTypesChoices.SIGN_OUT
                obj.check_out_by = timezone.now()
                obj.save()
                cls.message = f"{tmp_student['reg_number']} checked out"
            return True

    @classmethod
    def log_failed_attempt(cls, app_config: AppConfigParser):
        """This method will block a student after they attempt to
        log attendance 4 times unsuccessfully.
        """

        if "failed_attempts" not in app_config:
            app_config["failed_attempts"] = {}

        student_reg_number = app_config["tmp_student"]["reg_number"]
        failed_attempts = app_config["failed_attempts"]

        if student_reg_number not in failed_attempts:
            failed_attempts[student_reg_number] = str(1)
            app_config.save()

        elif failed_attempts.getint(student_reg_number) >= 3:
            if (
                "blocked_reg_numbers"
                not in app_config["current_attendance_session"]
            ):
                app_config["current_attendance_session"][
                    "blocked_reg_numbers"
                ] = ""
            app_config["current_attendance_session"]["blocked_reg_numbers"] += (
                "," + student_reg_number
            )
            app_config.save()
        else:
            failed_attempts[student_reg_number] = str(
                failed_attempts.getint(student_reg_number) + 1
            )
            app_config.save()
