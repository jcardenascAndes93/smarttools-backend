from django.contrib import admin
from .models import Concurso, UserVideo
# Register your models here.

Models = [Concurso, UserVideo]
admin.site.register(Models)
