from datetime import datetime

from django.http import HttpResponse
from django.db.models import Q, F
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from openpyxl.writer.excel import save_virtual_workbook

from db.models import (
    AttendanceRecord,
    AttendanceSession,
    AttendanceSessionStatusChoices,
)
from app.appconfigparser import AppConfigParser
from .spreadsheets import generate_attendance_records_sheet

@login_required
def dashboard(request):
    template = "dashboard.html"
    return render(request, template, {})


class AttendanceRecordView(ListView):
    template_name = "attendancesession_list.html"
    paginate_by: int = 20
    model = AttendanceSession

    def get_queryset(self):
        queryset = AttendanceSession.objects.filter(initiator=self.request.user)
        return queryset


@login_required
def end_attendance_session(request, pk):
    app_config = AppConfigParser()

    if app_config.cp.has_option("current_attendance_session", "session_id"):
        if app_config.cp.get("current_attendance_session", "session_id") == pk:
            messages.add_message(
                request,
                messages.ERROR,
                "This is an active attendance session. It can only "
                "be ended on the primary attendance device.",
            )
        else:
            attendance_session = AttendanceSession.objects.get(id=pk)
            attendance_session.status = AttendanceSessionStatusChoices.ENDED
            attendance_session.save()
    else:
        messages.add_message(
            request, messages.ERROR, "Error. Something went wrong."
        )
    return HttpResponseRedirect(reverse("attendance"))


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
            "student__first_name",
            "student__last_name",
            "student__reg_number",
            "student__department__name",
            "check_in_by",
        )
    )

    if not qs.exists():
        message = {"details": "No attendance records were found for the event"}
        return render(request, template, message)
    
    wb = generate_attendance_records_sheet(attendance_session, qs)

    response = HttpResponse(
        content=save_virtual_workbook(wb),
        content_type="application/ms-excel",
        headers={
            f"Content-Disposition": "attachment; filename="
            f"{attendance_session.course.code} "
            f'Attendance {datetime.strftime(attendance_session.start_time, "%d-%m-%Y")}.xlsx'
        },
    )
    return response
