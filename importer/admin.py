from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Flight)
admin.site.register(Takeoff)
admin.site.register(Landing)
admin.site.register(Thermals)
admin.site.register(Glides)