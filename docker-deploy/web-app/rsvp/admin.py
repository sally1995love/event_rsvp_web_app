from django.contrib import admin
from .models import Question, Choice, Event, Permission, Response


# Register your models here.
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Event)
admin.site.register(Permission)
admin.site.register(Response)
