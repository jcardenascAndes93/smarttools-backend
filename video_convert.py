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


def config_s3(filename='db_conf.ini', section='s3'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to sqs
    s3 = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            s3[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))

    return s3


def config_bd(filename='db_conf.ini', section='mongoDb'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))

    return db


def get_connection_sqs():
    param = config_sqs()
    sqs = boto3.client('sqs', region_name=param['region_name'], aws_access_key_id=param['aws_access_key_id'],
                       aws_secret_access_key=param['aws_secret_access_key'])
    return sqs


def get_connection_s3():
    param = config_sqs()
    s3 = boto3.client('s3', region_name=param['region_name'], aws_access_key_id=param['aws_access_key_id'],
                      aws_secret_access_key=param['aws_secret_access_key'])
    return s3


def get_connection_bd():
    params = config_bd()
    client = MongoClient(params['host'])
    db_con = client.smarttoolsdb
    return db_con


def get_unproccessed_video():
    # Create SQS client
    sqs = get_connection_sqs()
    queue_url = config_sqs()['queue_url']

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=900,
        WaitTimeSeconds=0
    )

    try:
        messages = response['Messages']
        videos = messages[0]
        return videos
    except KeyError:
        print('No hay mensajes')
        return None


def proccess_video():
    videos = get_unproccessed_video()
    if videos is not None:
        receipt_handle = videos['ReceiptHandle']
        video = json.loads(videos['Body'])
        path = video['video_file']
        file_name = str(path).split('/')[1]
        get_video(file_name, path)
        output = file_name.split('.')
        output = output[0]
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")
        new_file_name = 'convert_' + now + output + '.mp4'
        logging.info(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S ") +
                     'converting video: {}'.format(file_name))
        subprocess.run("sh video_convert.sh {} {}".format(file_name, new_file_name), shell=True)

        if upload_file(new_file_name):
            delete_message(receipt_handle)
            subprocess.run("rm {}".format(new_file_name), shell=True)
            update_video_status_converted(video['id'], new_file_name)
            send_email(video['id'])
        logging.info(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S  ") +
                     'video converted: {}'.format(file_name))


def get_video(file_name, object_name):
    param = config_s3()
    media = str(param['converted_bucket']).split('/')
    object_name = media[0] + '/' + object_name
    s3 = get_connection_s3()
    print ('file_name' + file_name + '  object_name'+ object_name)
    try:
        s3.download_file(param['bucket_name'], object_name, file_name)
    except ClientError as e:
        print(e)


def delete_message(receipt_handle):
    sqs = get_connection_sqs()
    queue_url = config_sqs()['queue_url']
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )


def upload_file(file_name):
    param = config_s3()
    object_name = param['converted_bucket'] + file_name

    # Upload the file
    s3_client = get_connection_s3()
    bucket = param['bucket_name']
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def update_video_status_converted(_id, file_name):
    param = config_s3()
    object_name = param['converted_bucket'] + file_name

    mydb = get_connection_bd()
    mycol = mydb['concursos_uservideo']
    myquery = {'id': _id}
    newvalues = {"$set": {'video_converted': object_name, 'convert_state': 1}}

    mycol.update_one(myquery, newvalues)


def send_email(_id):
    email_conf = config_email()
    email_server = smtplib.SMTP(email_conf['server'], email_conf['port'])
    email_server.ehlo()
    email_server.starttls()
    email_server.ehlo()
    email_server.login(email_conf['account'], email_conf['password'])
    em = get_uservideo(_id)
    concurso = get_concurso(em['concurso_id'])
    body = """<body>
    <p>Hola %s queremos agradecerte por participar en el concurso %s. Ingresa al <a href="%s/%s">sitio web</a> del concurso para ver tu video.</p>
    <br>
    <p>Cordialmente el equio de SmartTools</p>
    </body>""" % (em['user_name'], concurso['name'], email_conf['base_url'], concurso['uniq_url'])

    msg = MIMEText(body, 'html')
    msg['Subject'] = "{} - Revisa tu participación en el concurso {}".format(str(em['user_name']), str(concurso['name']))

    try:
        email_server.sendmail(email_conf['sender'], str(
            em['user_email']), msg.as_string().encode("ascii", errors="ignore"))

        update_video_status_sended(_id)
    except smtplib.SMTPDataError as e:
        print(e)

    email_server.close()


def config_email(filename='db_conf.ini', section='ses_aws'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    email = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            email[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))

    return email


def get_uservideo(_id):

    mydb = get_connection_bd()
    mycol = mydb['concursos_uservideo']
    myquery = {'id': _id}

    uservideo = mycol.find_one(myquery)
    return uservideo


def get_concurso(_id):

    mydb = get_connection_bd()
    mycol = mydb['concursos_concurso']
    myquery = {'id': _id}

    concurso = mycol.find_one(myquery)
    return concurso

def update_video_status_sended(_id):

    mydb = get_connection_bd()
    mycol = mydb['concursos_uservideo']
    myquery = {'id': _id}
    newvalues = {"$set": {'email_send': 1}}

    mycol.update_one(myquery, newvalues)


proccess_video()
