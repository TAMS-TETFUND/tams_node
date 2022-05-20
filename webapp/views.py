import csv
from datetime import datetime

from django.http import HttpResponse
from django.db.models import Q, F, Value
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from db.models import AttendanceRecord, AttendanceSession


@login_required
def dashboard(request):
    template = "dashboard.html"
    return render(request, template, {})


@login_required
def attendance_records(request):
    template = "attendance_records.html"
    qs = AttendanceSession.objects.filter(
        initiator=request.user
    ).prefetch_related("course")
    return render(request, template, {"records": qs})


@login_required
def download_attendance(request, pk):
    template = "download.html"
    attendance_session = AttendanceSession.objects.get(id=pk)

    if (
        attendance_session.initiator is None
        or attendance_session.initiator.username != request.user.username
    ):
        message = {
            "details": "Permission denied. You did not initiate this attendance session."
        }
        return render(request, template, message)

    qs = (
        AttendanceRecord.objects.filter(
            Q(
                Q(attendance_session=attendance_session)
                & Q(attendance_session__initiator=request.user)
            )
        )
        .prefetch_related("student")
        .values(
            "student__first_name", "student__last_name", "student__reg_number"
        )
    )

    if not qs.exists():
        message = {"details": "No attendance records were found for the event"}
        return render(request, template, message)

    response = HttpResponse(
        content_type="text/csv",
        headers={
            f"Content-Disposition": "attachment; filename="
            f"{attendance_session.course.code} "
            f'Attendance {datetime.strftime(attendance_session.start_time, "%d-%m-%Y")}.csv'
        },
    )

    field_names = ["S/N", "Name", "Reg. Number"]
    attendance_writer = csv.DictWriter(response, fieldnames=field_names)
    attendance_writer.writerow(
        {
            "S/N": f'{attendance_session.course.code} Attendance {datetime.strftime(attendance_session.start_time, "%d-%m-%Y")}'
        }
    )
    attendance_writer.writeheader()
    for idx, row in enumerate(qs, 1):
        attendance_writer.writerow(
            {
                "S/N": idx,
                "Name": f'{row["student__last_name"].capitalize()} {row["student__first_name"].capitalize()}',
                "Reg. Number": row["student__reg_number"],
            }
        )

    return response
