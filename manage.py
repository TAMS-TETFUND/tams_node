import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def init_django():
    if settings.configured:
        return
    
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.auth',
	    	'django.contrib.contenttypes',
            'db'
        ],
        DATABASES={
            'default':{
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        },
        AUTH_USER_MODEL = 'db.AppUser',
        DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
    )
    django.setup()

if __name__ =="__main__":
    init_django()
    execute_from_command_line()
