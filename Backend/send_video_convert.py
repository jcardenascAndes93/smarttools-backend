import boto3
import subprocess
from pymongo import MongoClient
import datetime
import smtplib
import logging
import json
from configparser import ConfigParser
import email
from email.mime.text import MIMEText

from botocore.exceptions import ClientError

logging.basicConfig(filename='video_convert.log', level=logging.INFO)
db_con = None


def config_sqs(filename='db_conf.ini', section='sqs'):
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



def get_connection_sqs():
    param = config_sqs()
    sqs = boto3.client('sqs', region_name=param['region_name'], aws_access_key_id=param['aws_access_key_id'],
                       aws_secret_access_key=param['aws_secret_access_key'])
    return sqs


def set_unproccessed_video(adj):
    
    for i in range(adj):
        send_message()


def send_message():
    # Create SQS client
    sqs = get_connection_sqs()
    queue_url = config_sqs()['queue_url']

    # Receive message from SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={ },
        MessageBody=(
            '{"id": 5, "video_file": "videos/DLP_PART_2_768k.avi"}'
        )   
    )


set_unproccessed_video(20)
