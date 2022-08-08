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
from rest_framework.serializers import ModelSerializer
from __main__ import app_config

from db.models import (AttendanceSession,
                       AttendanceRecord,
                       AttendanceSessionStatusChoices,
                       NodeDevice, Staff,
                       Student, )


class AttendanceSessionSerializer(ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = "__all__"


class AttendanceRecordSerializer(ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = "__all__"


class NodeDataSynch:
    @classmethod
    def first_time_sync(cls, protocol: str = "http"):
        """
        method to be called to sync the server data with the node device
        on initial setup when connection has been made to the server

            :param ip:  the ip of the server when connection has been made
            :param port: the port the server is running
            :param protocol: the protocol used to access the server
        """

        ip, port = cls.get_server_details()
        server_endpoint = 'api/v1/node-devices/backup/'

        server_url = f'{protocol}://{ip}:{port}/{server_endpoint}'
        backup_file = 'server_backup.json'

        backup_data = cls.sync_request(server_url, cls.get_header(), get=True)

        # Serializing json response
        json_object = json.dumps(backup_data.json(), indent=2)

        # Writing to back up file
        with open(backup_file, "w") as outfile:
            outfile.write(json_object)

        # load the data into node's database
        call_command('loaddata', backup_file)

        # clear the backup file
        os.remove(backup_file)

        # delete records that are not required
        Student.objects.filter(is_active=False).delete()
        Staff.objects.filter(is_active=False).delete()

    @classmethod
    def node_register(cls, headers: dict, json_data: dict, protocol: str = "http", ):
        ip, port = cls.get_server_details()
        endpoint = "api/v1/node-devices/"
        url = f'{protocol}://{ip}:{port}/{endpoint}'

        response = NodeDataSynch.sync_request(url, headers, json_data)

        return response.json()

    @classmethod
    def node_sync(cls, protocol: str = "http"):
        """
        method sends attendance session and the attendance record of the node device
        to the server
        @required attendance session has to be sent first before attendance record
        there is need to have a unique identifier of the attendance record that is not the
        auto increment integer primary key
        """

        ip, port = cls.get_server_details()
        endpoint = "api/v1/attendance/"

        url = f'{protocol}://{ip}:{port}/{endpoint}'

        headers = cls.get_header()

        sessions = AttendanceSession.objects.filter(status=AttendanceSessionStatusChoices.ENDED)
        sync_data = []

        # sync the attendance session first
        for session in sessions:
            sync_data.append(AttendanceSessionSerializer(session).data)

        cls.sync_request(url, headers, sync_data)

        # sync the records for each attendance session
        # after successful attendance session syncing
        sync_data.clear()
        endpoint = "api/v1/attendance/records/"
        url = f'{protocol}://{ip}:{port}/{endpoint}'

        for session in sessions:
            records = session.attendancerecord_set.all()
            for record in records:
                sync_data.append(AttendanceRecordSerializer(record).data)

        print(sync_data)
        cls.sync_request(url, headers, sync_data)

    @staticmethod
    def sync_request(url, headers, sync_data=None, get=False):
        try:
            if get:
                res = requests.get(url, headers=headers)
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
