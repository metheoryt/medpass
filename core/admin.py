from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from . import models


admin.site.register(User, UserAdmin)
admin.site.register(models.Place)
admin.site.register(models.CheckPoint)
admin.site.register(models.Region)
admin.site.register(models.Person)