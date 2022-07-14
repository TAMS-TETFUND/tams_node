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
import requests
import db.models

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


class NodeDataSych:
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
