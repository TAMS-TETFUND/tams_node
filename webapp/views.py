import csv
from datetime import datetime

from django.http import HttpResponse
from django.db.models import Q, F
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from db.models import AttendanceRecord, AttendanceSession, Staff

# Create your views here.

# @login_required
def dashboard(request):
    template = "dashboard.html"
    return render(request, template, {})


# @login_required
def attendance_records(request):
    template = "attendance_records.html"
    qs = (
        AttendanceSession.objects.filter(initiator=request.user)
        .prefetch_related("course")
        .values(
            "course__code",
            "course__title",
            "event_type",
            "start_time",
            "duration",
        )
    )
    return render(request, template, qs)


def download_attendance(pk, request):
    template = "download.html"
    attendance_session = AttendanceSession.objects.get(id=pk)
    qs = (
        AttendanceRecord.objects.filter(
            Q(
                attendace_session=attendance_session
                & Q(attendance_session__initiator=request.user)
            )
        )
        .prefetch_related("student")
        .values(
            "student__first_name", "student__last_name", "student_reg_number"
        )
    )

    if not qs.exists():
        message = {'details': "No attendance records were found for the event"}
        return render(request, template, message)

    field_names = ["S/N", "Name", "Reg. Number"]

    response = HttpResponse(
        content_type="text/csv",
        headers={
            'Content-Disposition': 'attachment; filename= '
            f'{attendance_session.course__code} '
            f'Attendance {datetime.strftime(attendance_session.start_time, "%d-%m-%Y")}'
        },
    )

    attendance_writer = csv.DictWriter(response, fieldnames=field_names)
    for idx, row in enumerate(qs, 1):
        attendance_writer.writerow(
            [
                idx,
                f'{row["student__last_name"].capitalize()} {row["student__first_name"].capitalize()}',
                row["student__reg_number"],
            ]
        )

    return response
