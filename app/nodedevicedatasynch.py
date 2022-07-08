"""
This module will handle the synching of data from the server to the db of 
node devices.

Could be designed as a class with methods to access the server API and SEQUENIALLY
populate the database of the node device. The sequence of the population is given 
below (This is to handle issue that may arise from foreign key relationships
between certain models.)
Due to the foreign key relationships, it may also be better to stop the 
synching if any problem is encountered with an API point. 

The address of the api point will be appended to the address of the server.

The address of the server will be entered by the user on the GUI. (the method will
have provision for this address to be passed to method performing the request.)
"""


model_sequence = [
    {"model":"StaffTitle", "url":"/staff/titles/"},
    {"model":"Faculty", "url":"/faculties"},
    {"model":"Department", "url":"/departments"},
    {"model":"Staff", "url":"/staff"},
    {"model":"Student", "url":"/students"},
    {"model":"Course", "url":"/courses"},
    {"model":"AcademicSession", "url":"/academic-sessions/"},
    {"model":"CourseRegistration", "url":"/course-registrations"}
]
