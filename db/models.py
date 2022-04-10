import re
from pathlib import Path
import os
import json
import numpy as np

from django.db.models import Value
from django.db.models.functions import Upper, Replace
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from manage import init_django

init_django()


#configuring the staff_number and studnet reg number format
config_file_path = os.path.join(Path(os.path.abspath(__file__)).parent.parent.parent, "config.json")

if not os.path.exists(config_file_path):
    raise FileNotFoundError("File: config.json not found")

with open(config_file_path, "r") as data:
    config_dict = json.loads(data.read())

STAFF_NO_FORMAT = r"{}".format(config_dict["STAFF_NO_FORMAT"])
STUDENT_REG_NO_FORMAT = r"{}".format(config_dict["STUDENT_REG_NO_FORMAT"])
SESSION_FORMAT = r"{}".format(config_dict["SESSION_FORMAT"])


class Semester(models.IntegerChoices):
    FIRST = 1, 'First Semester'
    SECOND = 2, 'Second Semester'


class Sex(models.IntegerChoices):
    MALE = 1, 'Male'
    FEMALE = 2, 'Female'


class StaffTitle(models.Model):
    id = models.BigAutoField(primary_key=True)
    title_full = models.CharField(max_length=50)
    title = models.CharField(max_length=25)


    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(Upper(Replace('title', Value('.'), Value(''))), name='unique_title')
        ]

    def __str__(self):
        return f"{self.title}"


class Faculty(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)


    class Meta:
        constraints = [
            models.UniqueConstraint(Upper('name'), name='unique_faculty_name')
        ]

class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    alias = models.CharField(max_length=20, null=True, blank=True)
    faculty = models.ForeignKey(to=Faculty, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(Upper('name'), name='unique_department_name'),
            models.UniqueConstraint(Upper('alias'), name='unique_department_short_name')
        ]


class AppUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    other_names = models.CharField(max_length=255, null=True, blank=True)
    fingerprint_template = models.CharField(max_length=3000, null=True, blank=True)
    face_encodings = models.CharField(max_length=3000, null=True, blank=True)


class Staff(AppUser):
    staff_number = models.CharField(max_length=25, unique=True)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    is_exam_officer = models.BooleanField(default=False)
    staff_titles = models.ManyToManyField(StaffTitle)

    def clean(self):
        self.staff_number = self.staff_number.upper()
        if not Staff.is_valid_staff_number(self.staff_number):
            raise ValidationError({'staff_number':'Invalid staff number provided'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def is_valid_staff_number(staff_no):
        return bool(re.search(STAFF_NO_FORMAT, staff_no.upper()))


class AppAdmin(AppUser):
    clearance_number = models.IntegerField(default=1)


class Student(models.Model):


    class AdmissionStatus(models.IntegerChoices):
        REGULAR = 1, 'Regular'
        GRADUATE = 2, 'Graduated'
        EXTERNAL = 3, 'External'
        OVERSTAY = 4, 'Overstay'
        WITHDRAWN = 5, 'Withdrawn'
        SUSPENDED = 6, 'Suspended'
    

    id = models.BigAutoField(primary_key=True)
    reg_number = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    other_names = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    possible_grad_yr = models.IntegerField()
    admission_status = models.IntegerField(choices=AdmissionStatus.choices, default=AdmissionStatus.REGULAR)
    level_of_study = models.IntegerField(null=True, blank=True)
    fingerprint_template = models.CharField(max_length=512, null=True, blank=True)
    face_encodings = models.CharField(max_length=3000, null=True, blank=True)
    sex = models.IntegerField(choices=Sex.choices)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.reg_number}), {self.admission_status}"

    @staticmethod
    def face_enc_to_str(encodings):
        """Convert face encodings from numpy array to string"""
        encodings_str = ','.join(str(item) for item in encodings)
        return encodings_str
    
    @staticmethod
    def str_to_face_enc(enc_str):
        """Convert encodings formatted as a string to numpy array"""
        encodings = np.array([float(item) for item in enc_str.split(',')])
        return encodings

    def clean(self):
        if not Student.is_valid_student_reg_number(self.reg_number):
            raise ValidationError(
                {'reg_number':'Invalid student registration number provided'})

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def is_valid_student_reg_number(reg_no):
        return bool(re.search(STUDENT_REG_NO_FORMAT, reg_no))


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=8)
    title = models.CharField(max_length=255)
    unit_load = models.IntegerField()
    semester = models.IntegerField(Semester.choices)
    elective = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code', 'title', 'unit_load'], name='unique_course_details')
        ]

    def clean(self):
        semester_list = [a for a, b in (item for item in Semester.choices)]
        if self.semester not in semester_list:
            raise ValidationError(
                {'semester': 'Invalid semester value'}
            )

    def save(self, *args, **kwargs):
        self.clean()
        return super(Course, self).save(*args, **kwargs)


class AcademicSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    session = models.CharField(max_length=10, unique=True)
    is_current_session = models.BooleanField(default=False)


    def clean(self):
        if not AcademicSession.is_valid_session(self.session):
            raise ValidationError(
                {'session': 'Invalid session value'}
            )

    def save(self, *args, **kwargs):
        self.clean
        if self.is_current_session:
            qs = type(self).objects.filter(is_current_session=True)

            if self.pk:
                qs = qs.exclude(pk=self.pk)

            qs.update(is_current_session=False)
#       super(AcademicSession, self).save(*args, **kwargs)
        super().save(*args, **kwargs)

    @staticmethod
    def is_valid_session(session):
        if re.search(SESSION_FORMAT, session):
            session_yrs = session.split('/')
            if (int(session_yrs[1]) - int(session_yrs[0])) == 1:
                return True
        return False


class AttendanceSession(models.Model):

    class EventType(models.IntegerChoices):
        LECTURE = 1, 'Lecture'
        LAB = 2, 'Lab'
        QUIZ = 3, 'Quiz/Continuous Assessment'
        EXAMINATION = 4, 'Examination'

    id = models.BigAutoField(primary_key=True)
    initiator = models.ForeignKey(to=AppUser, on_delete=models.CASCADE)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    session = models.ForeignKey(to=AcademicSession, on_delete=models.CASCADE)
    event_type = models.IntegerField(EventType.choices)
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'session', 'start_time','stop_time'],
                                name="unique_attendance_session")
        ]


    def clean(self):
        if (self.stop_time != None) and (self.start_time != None):
            if self.stop_time < self.start_time:
                raise ValueError(
                    {'stop_time': "Stop time cannot be set to be earlier than start time"}
                )

    def save(self, *args, **kwargs):
        self.clean()
        return super(AttendanceSession, self).save(*args, **kwargs)


class AttendanceRecord(models.Model):    

    class RecordTypes(models.IntegerChoices):
        SIGN_IN = 1, 'Sign In'
        SIGN_OUT = 2, 'Sign Out'

    id = models.BigAutoField(primary_key=True)
    attendance_session = models.ForeignKey(to=AttendanceSession, on_delete=models.CASCADE)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)
    record_type = models.IntegerField(RecordTypes.choices)
    logged_by = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default = True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['attendance_session', 'student',
                                            'record_type'], name="unique_attendance_record")
        ]


class CourseRegistration(models.Model):
    id = models.BigAutoField(primary_key=True)
    session = models.ForeignKey(to=AcademicSession, on_delete=models.CASCADE)
    semester = models.IntegerField(Semester.choices)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'course', 'session'], name="unique_course_registration")
        ]

    def clean(self):
        if self.semester != self.course.semester:
            raise ValidationError(
                {"semester": "Course is not offered in selected semester"}
            )

    def save(self, *args, **kwargs):
        self.clean()
        return super(CourseRegistration, self).save(*args, **kwargs)