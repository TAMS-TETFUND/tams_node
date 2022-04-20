import os
import time
from pathlib import Path
from configparser import ConfigParser

# from picamera.array import PiRGBArray
# from picamera import PiCamera
import cv2
import face_recognition
import numpy as np

from manage import init_django

init_django()

from db.models import (
    Student,
    Staff,
    Course,
    AcademicSession,
    Faculty,
    Semester,
    Department,
)

CURRENT_DIR = os.path.abspath(__file__)
CONFIG_FILE = os.path.join(Path(CURRENT_DIR).parent, "config.ini")
app_config = ConfigParser()
app_config.read(CONFIG_FILE)


def get_semesters():
    return Semester.labels


def get_all_courses(semester):
    all_courses = Course.objects.filter(
        semester=Semester.values[Semester.labels.index(semester)]
    ).exclude(is_active=False)
    return [f"{item.code} - {item.title}" for item in all_courses]


def get_all_academic_sessions():
    return list(
        AcademicSession.objects.all()
        .order_by("-is_current_session")
        .values_list("session", flat=True)
    )


def get_all_faculties():
    return list(
        Faculty.objects.all().order_by("name").values_list("name", flat=True)
    )


def get_all_departments():
    return list(
        Department.objects.all().order_by("name").values_list("name", flat=True)
    )


def filter_departments(faculty_name):
    return list(
        Department.objects.filter(faculty__name=faculty_name).values_list(
            "name", flat=True
        )
    )


def filter_courses(dept):
    if dept:
        course_list = list(
            Course.objects.filter(department__name=dept).exclude(
                is_active=False
            )
        )
        return [f"{item.code} - {item.title}" for item in course_list]
    else:
        get_all_courses()


def staff_face_verification(captured_image):
    """Staff Facial identification"""
    try:
        staff_number = app_config["new_event"]["initiator_staff_num"]
    except:
        print("something went wrong")

    try:
        staff = Staff.objects.get(staff_number=staff_number)
    except:
        print(f"No staff registered with staff number {staff_number}")

    staff_face_enc = Student.str_to_face_enc(staff.face_encodings)


def staff_fingerprint_verification():
    pass
