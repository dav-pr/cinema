from django.contrib import admin
from .models import Cinema, Seats, Hall

# Register your models here.
admin.site.register(Cinema)
admin.site.register(Hall)
admin.site.register(Seats)
