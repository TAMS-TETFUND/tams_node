"""
This module will handle the synching of data from the server to the db of 
node devices.

Could be designed as a class with methods to access the server API and SEQUENIALLY
populate the database of the node device. The sequence of the population is given 
below (This is to handle issue that may arise from foreign key relationships
between certain models.)
Due to the foreign key relationships, it may also be better to stop/restart the 
synching if any problem is encountered with an API point. 

The address of the api point will be appended to the address of the server.

The address of the server will be entered by the user on the GUI. (the method will
have provision for this address to be passed to method performing the request.)
"""
import json
import os

import requests
from django.core.management import call_command
from requests import HTTPError
from __main__ import app_config
from app.serializers import AttendanceRecordSerializer, AttendanceSessionSerializer, StaffSerializer, StudentSerializer
from db.models import Student, Staff, AttendanceSession, AttendanceSessionStatusChoices, NodeDevice


class NodeDataSynch:
    @classmethod
    def start_data_sync(cls, protocol: str = "http"):
        """
        method to be called to sync the server data with the node device
        on initial setup when connection has been made to the server

            :param ip:  the ip of the server when connection has been made
            :param port: the port the server is running
            :param protocol: the protocol used to access the server
        """
        server_endpoint = 'api/v1/node-devices/backup/'

        server_url = cls.get_url(server_endpoint, protocol=protocol)
        backup_file = 'server_backup.json'

        backup_data = cls.sync_request(server_url, cls.get_header(), get=True)

        response = requests.get(server_url)
        if response.status_code != 200:
            raise RuntimeError("Synch not successful (%d)" % response.status_code)
        # backup_data = requests.get(server_url).json()
        backup_data = response.json()
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
    def node_register(cls, headers: dict, json_data: dict, protocol: str = "http", ):
        endpoint = "api/v1/node-devices/"
        url = cls.get_url(endpoint, protocol=protocol)

        response = NodeDataSynch.sync_request(url, headers, json_data)

        return response.json()

    @classmethod
    def node_attendance_sync(cls, protocol: str = "http"):
        """
        method sends attendance session and the attendance record of the node device
        to the server
        @required attendance session has to be sent first before attendance record
        there is need to have a unique identifier of the attendance record that is not the
        auto increment integer primary key
        """

        endpoint = "api/v1/attendance/"

        url = cls.get_url(endpoint=endpoint, protocol=protocol)

        headers = cls.get_header()

        sessions = AttendanceSession.objects.filter(
            status=AttendanceSessionStatusChoices.ENDED,
            sync_status=False,
        )
        sync_data = []

        # sync the attendance session first
        for session in sessions:
            sync_data.append(AttendanceSessionSerializer(session).data)

        cls.sync_request(url, headers, sync_data)

        # sync the records for each attendance session
        # after successful attendance session syncing
        sync_data.clear()
        endpoint = "api/v1/attendance/records/"
        url = cls.get_url(endpoint)

        for session in sessions:
            records = session.attendancerecord_set.all()
            for record in records:
                sync_data.append(AttendanceRecordSerializer(record).data)

        print(sync_data)
        cls.sync_request(url, headers, sync_data)

        for session in sessions:
            session.sync_status = True
            session.save()

    @staticmethod
    def sync_request(url, headers, sync_data=None, get=False, put=False):
        try:
            if get:
                res = requests.get(url, headers=headers)
            elif put:
                res = requests.put(url, headers=headers, json=sync_data)
            else:
                res = requests.post(url, headers=headers, json=sync_data)
        except requests.exceptions.RequestException as e:
            raise HTTPError('{"detail": "Connection refused!"}')

        if res.status_code not in (201, 200):
            raise HTTPError(res.text)

        return res

    @classmethod
    def get_server_details(cls):
        try:
            ip = str(app_config.get("server_details", "server_ip_address"))
            port = app_config.getint("server_details", "server_port")
        except Exception:
            raise HTTPError('{"detail": "Server IP and port not set!"}')

        return ip, port

    @classmethod
    def get_header(cls):
        node = NodeDevice.objects.all().first()

        if node is None:
            raise HTTPError('{"detail": "Device not registered!"}')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token  {node.token} {node.id}"
        }
        return headers

    @classmethod
    def get_url(cls, endpoint, protocol='http', ip=None, port=None):
        if ip is None or port is None:
            ip, port = cls.get_server_details()

        url = f'{protocol}://{ip}:{port}/{endpoint}'
        return url

    @classmethod
    def staff_register(cls, staff_dict):
        staff_exist = Staff.objects.filter(staff_number=staff_dict['staff_number']).first()

        if staff_exist:
            ser_data = StaffSerializer(staff_exist, data=staff_dict)
            endpoint = f'api/v1/staff/{staff_exist.staff_number}/'
            put = True
            return_text = "Staff Updated successfully!"
        else:
            ser_data = StaffSerializer(data=staff_dict)
            endpoint = "api/v1/staff/"
            put = False
            return_text = "Staff Registered successfully!"

        if ser_data.is_valid():
            headers = cls.get_header()
            url = cls.get_url(endpoint, protocol='http')
            cls.sync_request(url, headers, staff_dict, put=put)
            cls.start_data_sync()
            return return_text
        raise HTTPError('{"detail": "Device not registered!"}')

    @classmethod
    def student_register(cls, student_dict):
        student_exist = Student.objects.filter(reg_number=student_dict['reg_number']).first()

        if student_exist:
            ser_data = StudentSerializer(student_exist, data=student_dict)
            endpoint = f'api/v1/students/{student_exist.reg_number}/'
            put = True
            return_text = "Student Updated successfully!"
        else:
            ser_data = StudentSerializer(data=student_dict)
            endpoint = "api/v1/students/"
            put = False
            return_text = "Student Registered successfully!"

        if ser_data.is_valid():
            headers = cls.get_header()
            url = cls.get_url(endpoint, protocol='http')
            cls.sync_request(url, headers, student_dict, put=put)
            cls.start_data_sync()
            return return_text
        raise HTTPError('{"detail": "Device not registered!"}')
