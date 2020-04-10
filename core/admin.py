from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group
from . import models, forms
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = forms.UserCreationForm
    form = forms.UserChangeForm
    list_display = UserAdmin.list_display + ('checkpoint', )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Inspector profile'), {'fields': ('checkpoint', )})
    )


admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.Checkpoint)
admin.site.register(models.CheckpointPass)
admin.site.register(models.PersonPassData)
admin.site.register(models.Region)
admin.site.register(models.Person)
admin.site.register(models.Marker)
admin.site.register(models.Country)
admin.site.register(models.Camera)
admin.site.register(models.CameraCapture)
