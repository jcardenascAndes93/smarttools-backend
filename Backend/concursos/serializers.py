from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField
from .models import Concurso, UserVideo


class ConcursoSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Concurso
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVideo
        fields = (
            'user_name',
            'user_lastname',
            'user_email',
            'video_file',
            'message',
            'video_converted',            
            'upload_date',
            'convert_state'
        )


class SimpleConcursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concurso
        fields = (
            'name',
            'image',
            'start_date',
            'end_date',
            'prize_description'
        )
