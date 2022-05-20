from datetime import timedelta

from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError

from manage import django_setup

django_setup()

from .models import (
    Faculty,
    StaffTitle,
    Department,
    Staff,
    Student,
    Semester,
    Course,
    AcademicSession,
    AttendanceRecord,
    AttendanceSession,
    CourseRegistration,
    Sex,
    EventType,
    RecordTypes,
)


class SemesterTestCase(TestCase):
    def test_semester_vals(self):
        self.assertEqual(Semester.FIRST, 1)
        self.assertEqual(Semester.SECOND, 2)


class FacultyTestCase(TestCase):
    def setUp(self):
        Faculty.objects.create(name="Engineering")

    def test_successful_faculty_creation(self):
        engr = Faculty.objects.get(name="Engineering")
        self.assertEqual(engr.name, "Engineering")

    def test_unique_faculty_constraint(self):
        """test creating a duplicate Faculty object"""
        self.assertRaises(
            IntegrityError, Faculty.objects.create, name="engineering"
        )


class StaffTitleTestCase(TestCase):
    def setUp(self):
        StaffTitle.objects.create(title="Prof", title_full="Professor")

    def test_unique_title_constraint(self):
        """Test creating a duplicate StaffTitle object"""
        self.assertRaises(
            IntegrityError,
            StaffTitle.objects.create,
            **{"title": "Prof.", "title_full": "Professor"}
        )

    def test_anycase_unique_title_constraint(self):
        self.assertRaises(
            IntegrityError,
            StaffTitle.objects.create,
            **{"title": "prof", "title_full": "professor"}
        )


class DepartmentTestCase(TestCase):
    def setUp(self):
        engrng = Faculty.objects.create(name="Physical Sciences")
        Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=engrng
        )

    def test_unique_department_constraint(self):
        """Test creating a duplicate department object"""
        engrng2 = Faculty.objects.create(name="Engineering")
        self.assertRaises(
            IntegrityError,
            Department.objects.create,
            **{
                "name": "electronic engineering",
                "alias": "ece",
                "faculty": engrng2,
            }
        )

    def test_unique_dept_short_name(self):
        """Test creating a department object with identical alias as
        an existing object
        """
        self.assertRaises(
            IntegrityError,
            Department.objects.create,
            **{
                "name": "elect. engr.",
                "alias": "ece",
                "faculty": Faculty.objects.get(name="Physical Sciences"),
            }
        )


class StaffTestCase(TestCase):
    def test_staff_number_validation(self):
        self.assertTrue(Staff.is_valid_staff_number("SS.123456"))
        self.assertTrue(Staff.is_valid_staff_number("ss.123456"))

    def test_custom_clean(self):
        """Testing the custom clean method of the Staff class"""
        new_title = StaffTitle.objects.create(title="Mr")
        dept = Department.objects.create(
            name="Electronic",
            alias="ece",
            faculty=Faculty.objects.create(name="engineering"),
        )
        new_staff = Staff.objects.create_user(
            email="example@example.com",
            username="demo_user",
            first_name="John",
            last_name="Doe",
            other_names="Lorem",
            fingerprint_template="77777777",
            face_encodings="XXXXXXXXX",
            staff_number="ss.123456",
            department=dept,
        )
        new_staff.staff_titles.add(new_title)
        self.assertEqual(new_staff.staff_number, "SS.123456")
        self.assertFalse(new_staff.is_exam_officer)
        self.assertFalse(new_staff.is_superuser)

    def test_duplicate_staff_number_prevention(self):
        """Attempting to create two Staff records with the same staff number"""
        new_title = StaffTitle.objects.create(title="Mr")
        dept = Department.objects.create(
            name="Electronic",
            alias="ece",
            faculty=Faculty.objects.create(name="engineering"),
        )
        new_staff = Staff.objects.create_user(
            email="example@example.com",
            username="demo_user",
            first_name="John",
            last_name="Doe",
            other_names="Lorem",
            fingerprint_template="77777777",
            face_encodings="XXXXXXXXX",
            staff_number="ss.123456",
            department=dept,
        )
        new_staff.staff_titles.add(new_title)

        new_title2 = StaffTitle.objects.create(title="Mrs")
        dept2 = Department.objects.create(
            name="mathematics",
            alias="eee",
            faculty=Faculty.objects.create(name="physical sciences"),
        )
        staff2_dict = {
            "email": "example2@example.com",
            "username": "demo_user2",
            "first_name": "Jane",
            "last_name": "Doe",
            "other_names": "Lorem",
            "fingerprint_template": "8888888888",
            "face_encodings": "YYYYYYYYYY",
            "staff_number": "ss.123456",
            "department": dept2,
        }
        self.assertRaises(
            ValidationError, Staff.objects.create_user, **staff2_dict
        )


class StudentTestCase(TestCase):
    def test_reg_number_validation(self):
        """Testing the Student.is_valid_student_reg_number with
        various values of student registration numbers
        """
        self.assertTrue(Student.is_valid_student_reg_number("1999/123456"))
        self.assertFalse(Student.is_valid_student_reg_number("99/123456"))
        self.assertFalse(Student.is_valid_student_reg_number("123456"))
        self.assertFalse(Student.is_valid_student_reg_number("99_123456"))
        self.assertFalse(Student.is_valid_student_reg_number("'99/123456"))


class CourseTestCase(TestCase):
    def test_unique_course_details_constraint(self):
        """Attempting to create 2 courses with the same title, code, and
        unit load"""
        new_faculty = Faculty.objects.create(name="Engineering")
        new_dept = Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=new_faculty
        )
        new_course = Course.objects.create(
            code="ECE 272",
            title="Introduction to Engineering Programming",
            level_of_study=2,
            department=new_dept,
            unit_load=3,
            semester=Semester.SECOND,
        )
        course_details = {
            "code": "ECE 272",
            "title": "Introduction to Engineering Programming",
            "level_of_study": 2,
            "department": new_dept,
            "unit_load": 3,
            "semester": Semester.SECOND,
        }
        self.assertRaises(
            IntegrityError, Course.objects.create, **course_details
        )

    def test_semester_field_validation_constraint(self):
        """Attempting to create a course with semester set to value not defined
        in Semester class
        """
        new_faculty = Faculty.objects.create(name="Engineering")
        new_dept = Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=new_faculty
        )
        course_details = {
            "code": "ECE 273",
            "title": "Introduction to Engineering Programming",
            "level_of_study": 2,
            "department": new_dept,
            "unit_load": 3,
            "semester": 3,
        }
        self.assertRaises(
            IntegrityError, Course.objects.create, **course_details
        )


class AcademicSessionTestCase(TestCase):
    def setUp(self):
        AcademicSession.objects.create(
            session="2019/2020", is_current_session=True
        )

    def test_session_format(self):
        """Test session validation method"""
        self.assertTrue(AcademicSession.is_valid_session("2020/2021"))
        self.assertFalse(AcademicSession.is_valid_session("2001_2002"))
        self.assertFalse(AcademicSession.is_valid_session("2001/2003"))

    def test_is_current_session_change(self):
        """Ensure that when a new AcademicSession object is marked as current session,
        only that object and no other is marked as current session
        """
        AcademicSession.objects.create(
            session="2020/2021", is_current_session=True
        )
        current_session = AcademicSession.objects.get(
            is_current_session=True
        ).session
        self.assertEqual(current_session, "2020/2021")

    def test_duplicate_session_creation(self):
        """Test duplicate session creation"""
        session_details = {"session": "2019/2020", "is_current_session": False}
        self.assertRaises(
            IntegrityError, AcademicSession.objects.create, **session_details
        )


class AttendanceSessionTestCase(TestCase):
    def test_duplicate_attendance_session_creation(self):
        """Test duplicate attendance session creation"""
        faculty_obj = Faculty.objects.create(name="Engineering")
        dept_obj = Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=faculty_obj
        )
        staff_obj = Staff.objects.create_user(
            username="Danladi",
            first_name="John",
            last_name="Doe",
            email="example@example.com",
            other_names="Lorem",
            staff_number="SS.123654",
            department=dept_obj,
        )
        acad_session = AcademicSession.objects.create(
            session="2020/2021", is_current_session=True
        )
        course_obj = Course.objects.create(
            code="ECE 272",
            title="Introduction to Engineering Programming",
            level_of_study=2,
            department=dept_obj,
            unit_load=3,
            semester=Semester.SECOND,
        )
        start_time = timezone.now()
        att_session = AttendanceSession.objects.create(
            initiator=staff_obj,
            course=course_obj,
            session=acad_session,
            event_type=EventType.LECTURE,
            start_time=start_time,
            duration=timedelta(hours=2),
        )
        att_session_details = {
            "initiator": staff_obj,
            "course": course_obj,
            "session": acad_session,
            "event_type": EventType.LECTURE,
            "start_time": start_time,
            "duration": timedelta(hours=2),
        }
        self.assertRaises(
            IntegrityError,
            AttendanceSession.objects.create,
            **att_session_details
        )

    def test_start_stop_time_validation(self):
        faculty_obj = Faculty.objects.create(name="Engineering")
        dept_obj = Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=faculty_obj
        )
        staff_obj = Staff.objects.create_user(
            username="Danladi",
            first_name="John",
            last_name="Doe",
            email="example@example.com",
            other_names="Lorem",
            staff_number="SS.123654",
            department=dept_obj,
        )
        acad_session = AcademicSession.objects.create(
            session="2020/2021", is_current_session=True
        )
        course_obj = Course.objects.create(
            code="ECE 272",
            title="Introduction to Engineering Programming",
            level_of_study=2,
            department=dept_obj,
            unit_load=3,
            semester=Semester.SECOND,
        )
        start_time = timezone.now()
        # attempting to set stop time to be earlier than start time
        att_session_details = {
            "initiator": staff_obj,
            "course": course_obj,
            "session": acad_session,
            "event_type": EventType.LECTURE,
            "start_time": start_time,
            "duration": timedelta(microseconds=0),
        }
        self.assertRaises(
            IntegrityError,
            AttendanceSession.objects.create,
            **att_session_details
        )


class AttendanceRecordTestCase(TestCase):
    def test_duplicate_att_record_creation(self):
        """Atempt to sign same student in twice"""
        faculty_obj = Faculty.objects.create(name="Engineering")
        dept_obj = Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=faculty_obj
        )
        staff_obj = Staff.objects.create_user(
            username="Danladi",
            first_name="John",
            last_name="Doe",
            email="example@example.com",
            other_names="Lorem",
            staff_number="SS.123654",
            department=dept_obj,
        )
        acad_session = AcademicSession.objects.create(
            session="2020/2021", is_current_session=True
        )
        course_obj = Course.objects.create(
            code="ECE 272",
            title="Introduction to Engineering Programming",
            level_of_study=2,
            department=dept_obj,
            unit_load=3,
            semester=Semester.SECOND,
        )
        student_obj = Student.objects.create(
            reg_number="2001/123456",
            first_name="Chudi",
            last_name="Gambo",
            possible_grad_yr=2022,
            level_of_study=2,
            department=dept_obj,
            sex=Sex.MALE,
        )
        att_session = AttendanceSession.objects.create(
            initiator=staff_obj,
            course=course_obj,
            session=acad_session,
            event_type=EventType.LECTURE,
            start_time=timezone.now(),
            duration=timedelta(hours=1),
        )

        AttendanceRecord.objects.create(
            attendance_session=att_session,
            student=student_obj,
            record_type=RecordTypes.SIGN_IN,
        )

        record_details = {
            "attendance_session": att_session,
            "student": student_obj,
            "record_type": RecordTypes.SIGN_IN,
        }
        self.assertRaises(
            IntegrityError, AttendanceRecord.objects.create, **record_details
        )


class CourseRegistrationTestCase(TestCase):
    def test_duplicate_course_reg(self):
        faculty_obj = Faculty.objects.create(name="Engineering")
        acad_session = AcademicSession.objects.create(
            session="2020/2021", is_current_session=True
        )
        dept_obj = Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=faculty_obj
        )
        course_obj = Course.objects.create(
            code="ECE 272",
            title="Introduction to Engineering Programming",
            level_of_study=2,
            department=dept_obj,
            unit_load=3,
            semester=Semester.SECOND,
        )
        student_obj = Student.objects.create(
            reg_number="2001/123456",
            first_name="Chudi",
            last_name="Gambo",
            possible_grad_yr=2022,
            level_of_study=2,
            department=dept_obj,
            sex=Sex.MALE,
        )

        CourseRegistration.objects.create(
            session=acad_session,
            semester=Semester.SECOND,
            course=course_obj,
            student=student_obj,
        )

        reg_details = {
            "session": acad_session,
            "semester": Semester.SECOND,
            "course": course_obj,
            "student": student_obj,
        }
        self.assertRaises(
            IntegrityError, CourseRegistration.objects.create, **reg_details
        )

    def test_semester_match_validation(self):
        faculty_obj = Faculty.objects.create(name="Engineering")
        acad_session = AcademicSession.objects.create(
            session="2020/2021", is_current_session=True
        )
        dept_obj = Department.objects.create(
            name="Electronic Engineering", alias="ECE", faculty=faculty_obj
        )
        course_obj = Course.objects.create(
            code="ECE 272",
            title="Introduction to Engineering Programming",
            level_of_study=2,
            department=dept_obj,
            unit_load=3,
            semester=Semester.SECOND,
        )
        student_obj = Student.objects.create(
            reg_number="2001/123456",
            first_name="Chudi",
            last_name="Gambo",
            possible_grad_yr=2022,
            level_of_study=2,
            department=dept_obj,
            sex=Sex.MALE,
        )

        reg_details = {
            "session": acad_session,
            "semester": Semester.FIRST,
            "course": course_obj,
            "student": student_obj,
        }
        # attempting to register a second semester course in First semester
        self.assertRaises(
            ValidationError, CourseRegistration.objects.create, **reg_details
        )
