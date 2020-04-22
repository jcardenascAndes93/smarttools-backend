from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import AdminUserChangeForm, AdminUserCreationForm
from .models import AdminUser


# Register your models here.

class AdminUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    model = AdminUser
    list_display = ['email', 'username',]

admin.site.register(AdminUser, AdminUserAdmin)

