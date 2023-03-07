from django.contrib import admin
from .models import Cinema, Raw, Seats, Hall

# Register your models here.
admin.site.register(Cinema)
admin.site.register(Hall)
admin.site.register(Raw)
admin.site.register(Seats)
