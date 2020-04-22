from django.db import models
from accounts.models import AdminUser
from django.core.validators import FileExtensionValidator

# Create your models here.


class Concurso(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(blank=True, null=True, upload_to="banners/")
    uniq_url = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    prize_description = models.TextField(max_length=200)
    owner = models.ForeignKey(
        AdminUser, on_delete=models.CASCADE, related_name='administrador')

    def __str__(self):
        return self.name + ' - ' + str(self.owner)


# valid video extensions
video_ext = ['mp4', 'mov', 'flv', 'avi', 'wmv']


class UserVideo(models.Model):
    user_name = models.CharField(max_length=50)
    user_lastname = models.CharField(max_length=50)
    user_email = models.EmailField(verbose_name='user email')
    video_file = models.FileField(
        upload_to='videos/', validators=[FileExtensionValidator(allowed_extensions=video_ext)])
    message = models.TextField(max_length=100)
    video_converted = models.CharField(blank=True, max_length=114)
    convert_state = models.IntegerField(verbose_name='estado video', default=0)
    upload_date = models.DateField(auto_now_add=True)
    concurso = models.ForeignKey(Concurso, on_delete=models.CASCADE, related_name='concurso')
    email_send = models.IntegerField(verbose_name='estado email', default=0)

    def __str__(self):
        return str(self.concurso) + ' - ' + self.user_email
