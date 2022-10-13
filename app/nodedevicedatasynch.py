"""This module handles the synching of data from the server to the db of 
node devices.
"""
import json
import os
from typing import Any, Dict, Optional, Tuple

import requests
from django.core.management import call_command
from requests import HTTPError, Response
from app.appconfigparser import AppConfigParser
from app.nodedeviceinit import DeviceRegistration
from app.serializers import (
    AttendanceRecordSerializer,
    AttendanceSessionSerializer,
    StaffSerializer,
    StudentSerializer,
)
from app.serverconnection import ServerConnection
from db.models import (
    Student,
    Staff,
    AttendanceSession,
    AttendanceSessionStatusChoices,
    NodeDevice,
)

app_config = AppConfigParser()
server_conn = ServerConnection()

class NodeDataSynch:
    @classmethod
    def start_data_sync(cls, protocol: str = "http") -> None:
        """Sync server data to node device on completion of initial setup.

        :param ip:  the ip of the server when connection has been made
        :param port: the port the server is running
        :param protocol: the protocol used to access the server
        """
        server_endpoint = "api/v1/node-devices/backup/"

        backup_file = "server_backup.json"
        backup_data = server_conn.request(server_endpoint, get=True)

        # Serializing json response
        json_object = json.dumps(backup_data.json(), indent=2)

        # Writing to back up file
        with open(backup_file, "w") as outfile:
            outfile.write(json_object)

        # load the data into node's database
        call_command("loaddata", backup_file)

        # clear the backup file
        os.remove(backup_file)

        # delete records that are not required
        Student.objects.filter(is_active=False).delete()
        Staff.objects.filter(is_active=False).delete()

    @classmethod
    def node_register(
        cls,
        headers: Dict[str, str],
        json_data: Dict[str, Any],
        protocol: str = "http",
    ) -> Any:
        endpoint = "api/v1/node-devices/"
        response = server_conn.request(endpoint, json_data)
        return response.json()

    @classmethod
    def node_attendance_sync(cls, protocol: str = "http") -> None:
        """Send attendance session/record from the node device to server.

        Attendance session is sent first before attendance records because of a
        foreign key relationship between the attendance records and attendance
        sessions.
        """

        endpoint = "api/v1/attendance/"

        sessions = AttendanceSession.objects.filter(
            status=AttendanceSessionStatusChoices.ENDED,
            sync_status=False,
        )
        sync_data = []

        # sync the attendance session first
        for session in sessions:
            sync_data.append(AttendanceSessionSerializer(session).data)

        server_conn.request(endpoint, sync_data)

        # sync the records for each attendance session
        # after successful attendance session syncing
        sync_data.clear()
        endpoint = "api/v1/attendance/records/"

        for session in sessions:
            records = session.attendancerecord_set.all()
            for record in records:
                sync_data.append(AttendanceRecordSerializer(record).data)

        server_conn.request(endpoint, sync_data)

        for session in sessions:
            session.sync_status = True
            session.save()

    @classmethod
    def staff_register(cls, staff_dict: Dict[str, Any]) -> str:
        """Synch registration data of staff to server.

        Method handles both initial initial staff registration and
        update of existing staff.
        """
        staff = Staff.objects.filter(
            staff_number=staff_dict["staff_number"]
        ).first()

        if staff:
            ser_data = StaffSerializer(staff, data=staff_dict)
            endpoint = f"api/v1/staff/{staff.staff_number}/"
            put = True
            return_text = "Staff Updated successfully!"
        else:
            ser_data = StaffSerializer(data=staff_dict)
            endpoint = "api/v1/staff/"
            put = False
            return_text = "Staff Registered successfully!"

        if ser_data.is_valid():
            server_conn.request(endpoint, staff_dict, put=put)
            cls.start_data_sync()
            return return_text
        raise HTTPError('{"detail": "Device not registered!"}')

    @classmethod
    def student_register(cls, student_dict: Dict[str, Any]) -> str:
        """Synch registration data of student to server.

        Method handles both initial student registration and update
        of existing student.
        """
        if not DeviceRegistration.is_registered():
            raise HTTPError('{"detail": "Device not registered!"}')

        student = Student.objects.filter(
            reg_number=student_dict["reg_number"]
        ).first()

        if student:
            ser_data = StudentSerializer(student, data=student_dict)
            endpoint = f"api/v1/students/{student.reg_number}/"
            put = True
            return_text = "Student Updated successfully!"
        else:
            ser_data = StudentSerializer(data=student_dict)
            endpoint = "api/v1/students/"
            put = False
            return_text = "Student Registered successfully!"

        if ser_data.is_valid():
            server_conn.request(endpoint, student_dict, put=put)
            cls.start_data_sync()
            return return_text
        raise HTTPError('{"detail": "Something went wrong!"}')
