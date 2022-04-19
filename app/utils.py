import os

# from picamera.array import PiRGBArray
# from picamera import PiCamera
# from db.models import Student, Staff
import cv2
import face_recognition
import numpy as np
import time

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
    """Begin by getting all Staff objects that have face encodings to create the
    list for comparison

    Then, capture a picture with the camera. Ensuring that only one face is
        in the captured image

    Then, compare the image with all elements of the list created in (1) above
    Return the details of the best match (if any)
    """
    all_staff = list(
        Staff.objects.exclude(face_encodings__isnull=True).exclude(
            face_encodings__exact=""
        )
    )
    all_staff_face_enc = list(
        enc
        for enc in [
            Staff.str_to_face_enc(item.face_encodings) for item in all_staff
        ]
    )

    loaded_image_file = face_recognition.loaded_image_file(captured_image)
    if len(face_recognition.face_encodings(loaded_image_file)) > 1:
        pass
        # too many faces in the picture
    elif len(face_recognition.face_encodings(loaded_image_file)) <= 0:
        pass
        # no face in the picture
    elif len(face_recognition.face_encodings(loaded_image_file)) == 1:
        pass
        # exactly one face in the picture


def staff_fingerprint_verification():
    pass
