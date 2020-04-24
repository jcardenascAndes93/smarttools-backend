from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from django.shortcuts import get_object_or_404

from .models import Concurso, AdminUser, UserVideo
from .serializers import ConcursoSerializer, VideoSerializer, SimpleConcursoSerializer

import boto3
from configparser import ConfigParser
import os
import json

# Create your views here.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def config_sqs(filename=os.path.join(BASE_DIR, 'db_conf.ini'), section='sqs'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to sqs
    sqs = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            sqs[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))

    return sqs


def setMsgQueue(video_data):
    response = None
    # Connect to SQS queue
    #param = config_sqs()
    try:
        sqs = boto3.client('sqs', region_name=os.environ['SQS_REGION'], aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
        # Set msg
        queue_url = os.environ['SQS_URL_QUEUE']
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=10,
            MessageBody=(json.dumps(video_data))
        )
    except boto3.exceptions.Boto3Error as e:
        print(e)
    
    finally:
        if response:
            return response
        else:
            # Delete created UserVideo
            UserVideo.objects.get(pk=video_data['id']).delete()
            return response


class ListUserConcursosView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ConcursoSerializer

    def get_queryset(self):
        return Concurso.objects.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, pk=None):
        concurso = get_object_or_404(Concurso, id=pk)
        # check if request.user is owner
        if concurso.owner == self.request.user:
            videos = UserVideo.objects.order_by(
                '-upload_date').filter(concurso=pk)
            concurso_serializer = ConcursoSerializer(concurso)
            videos_serializer = VideoSerializer(videos, many=True)
            return Response({'concurso': concurso_serializer.data, 'videos': videos_serializer.data})

        else:
            return Response({'response': 'Owner unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, pk=None, **kwargs):
        concurso = get_object_or_404(Concurso, id=pk)
        # check if request.user is owner
        if concurso.owner == self.request.user:
            partial = kwargs.pop('partial', False)
            serializer = ConcursoSerializer(
                concurso, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

        else:
            return Response({'detail': 'Owner unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        concurso = get_object_or_404(Concurso, id=pk)
        # check if request.user is owner
        if concurso.owner == self.request.user:
            self.perform_destroy(concurso)
            return Response({'detail': 'Object deleted'}, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({'response': 'Owner unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class HomeConcursoView(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    parser_class = (FileUploadParser,)

    def retrieve(self, *args, **kwargs):
        # get concurso
        concurso_url = self.kwargs.get('concurso_url')
        concurso = get_object_or_404(Concurso, uniq_url=concurso_url)
        concurso_serializer = SimpleConcursoSerializer(concurso)
        videos = UserVideo.objects.order_by(
            '-upload_date').filter(concurso=concurso).filter(convert_state=True)
        videos_serializer = VideoSerializer(videos, many=True)
        return Response({'concurso': concurso_serializer.data, 'videos': videos_serializer.data})

    def perform_create(self, serializer):
        concurso_url = self.kwargs.get('concurso_url')
        concurso = get_object_or_404(Concurso, uniq_url=concurso_url)
        video = serializer.save(concurso=concurso)        
        print('=' * 60)
        print(video.pk)
        print(video.video_file)
        video_data = {"id": video.pk, "video_file": str(video.video_file)}
        return setMsgQueue(video_data)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queue = self.perform_create(serializer)
        if queue:
            headers = self.get_success_headers(serializer.data)        
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else: return Response('Operation cannot be prformed', status=status.HTTP_400_BAD_REQUEST)
        
        
