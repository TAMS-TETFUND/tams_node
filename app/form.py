import sys
sys.path.append(".")
import app.abbot
from manage import init_django
init_django()
from db.models import Faculty


new_fac = Faculty.objects.get(name="Engineering")

print(new_fac)