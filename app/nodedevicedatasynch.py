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
import os
import requests
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tams_node.settings")
# application = get_wsgi_application()
from requests import HTTPError
from rest_framework.serializers import ModelSerializer

from db.models import *

SERVER_ENDPOINT = 'api/v1/node-devices/backup/'  # TODO: update the url

model_sequence = [
    {"model": "StaffTitle", "url": "/staff/titles/"},
    {"model": "Faculty", "url": "/faculties"},
    {"model": "Department", "url": "/departments"},
    {"model": "Staff", "url": "/staff"},
    {"model": "Student", "url": "/students"},
    {"model": "Course", "url": "/courses"},
    {"model": "AcademicSession", "url": "/academic-sessions/"},
    {"model": "CourseRegistration", "url": "/course-registrations"},
]


class AttendanceSessionSerializer(ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = "__all__"


class AttendanceRecordSerializer(ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = "__all__"


class NodeDataSynch:
    @staticmethod
    def start_synch(server_address: str):
        for model in model_sequence:
            req = requests.get("http://%s%s" % (server_address, model["url"]))
            # You can get the list of data passed from the server with something like:
            # response_dict = req.json()
            # After getting the data sent, proceed to saving it the model
            # model["model"]. Use create_or_update to save modifications to
            # already existing data.
            # Ensure that the request(line 35) is ok first!!

    @staticmethod
    def first_time_sync(ip: str, port: int, protocol: str = "http"):
        """
        method to be called to sync the server data with the node device
        on initial setup when connection has been made to the server

            :param ip:  the ip of the server when connection has been made
            :param port: the port the server is running
            :param protocol: the protocol used to access the server
        """

        server_url = f'{protocol}://{ip}:{port}/{SERVER_ENDPOINT}'
        backup_file = 'server_backup.json'
        cls = ('AppUser', 'Student', 'Staff', 'Department')

        backup_data = requests.get(server_url).json()

        # Serializing json response
        json_object = json.dumps(backup_data, indent=2)

        # Writing to back up file
        with open(backup_file, "w") as outfile:
            outfile.write(json_object)

        # delete old records if any
        for c in cls:
            eval(c).objects.all().delete()

        # load the data into node's database
        call_command('loaddata', backup_file)

    @staticmethod
    def node_register(ip: str, port: int, headers: dict, json_data: dict, protocol: str = "http", ):
        endpoint = "api/v1/node-devices/"
        url = f'{protocol}://{ip}:{port}/{endpoint}'

        response = NodeDataSynch.sync_post(headers, json_data, url)

        return response.json()

    @staticmethod
    def node_sync(ip: str = '127.0.0.1', port: int = 8080, protocol: str = "http"):
        """
        method sends attendance session and the attendance record of the node device
        to the server
        @required attendance session has to be sent first before attendance record
        there is need to have a unique identifier of the attendance record that is not the
        auto increment integer primary key
        """

        endpoint = "api/v1/attendance/"
        url = f'{protocol}://{ip}:{port}/{endpoint}'
        headers = {
            "Content-Type": "application/json",
            "Authorization": "token  admin_1234567890 1"
        }

        sessions = AttendanceSession.objects.filter(status=AttendanceSessionStatusChoices.ENDED)
        sync_data = []

        # sync the attendance session first
        for session in sessions:
            sync_data.append(AttendanceSessionSerializer(session).data)

        NodeDataSynch.sync_post(headers, sync_data, url)

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
        NodeDataSynch.sync_post(headers, sync_data, url)

    @staticmethod
    def sync_post(headers, sync_data, url):
        try:
            res = requests.post(url, headers=headers, json=sync_data)
        except requests.exceptions.RequestException as e:
            raise HTTPError('{"detail": "Connection refused!"}')

        if res.status_code not in (201, 200):
            raise HTTPError(res.text)

        return res
