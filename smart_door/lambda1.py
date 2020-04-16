import json
import base64
import boto3
import botocore
import datetime
import random
from urllib.request import urlretrieve
from boto3.dynamodb.conditions import Key
import os
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import sys
sys.path.insert(1, '/opt')
import cv2

def lambda_handler(event, context):
    for record in event['Records']:
        decoded_data = json.loads(base64.b64decode(record['kinesis']['data']))
        faces = decoded_data['FaceSearchResponse']
        for face in faces:
            # known face case
            if face['MatchedFaces']:
                print("KNOWN FACE")
                for mf in face['MatchedFaces']:
                    faceId = mf['Face']['FaceId']
                    # if no record in DB, set record
                    if not hasRecord(faceId):
                        setRecord(faceId)
                    # make sure the person is not granted access, to prevent msg bombs
                    if not isAccessGranted(faceId):
                        visitor = getRecord(faceId)
                        # make sure the visitor is verified so we know the person's name and phone number in our DB
                        if isVerified(visitor):
                            passcode = generateOTP(faceId)
                            updateAccessTimeStamp(faceId)
                            msg = "Your One-Time Passcode is " + passcode
                            sendMsg(visitor['phoneNumber'], msg)
                        # if not verified, send verification, make sure it is sent only once
                        elif not isVerificationSent(visitor):
                            # send verification and if success, set the flag to true to prevent email bombs
                            if sendVerification(visitor['faceId']):
                                setVerification(faceId)
            # unknown face case
            else:
                print("UNKNOWN FACE")
                # extract faces since this photo may contain multiple faces 
                for f in getFacesFromStream():
                    cv2.imwrite('/tmp/tmp.jpg', f)
                    # upload to S3 so we can add to the collection
                    uploadToS3('/tmp/tmp.jpg', 'visitor-album', 'tmp.jpg')
                    results = addToCollection('faceCollection','visitor-album', 'tmp.jpg')
                    for result in results:
                        # write faces into files so that they can be emailed later
                        fileName = result['Face']['FaceId'] + '.jpg'
                        uploadToS3('/tmp/tmp.jpg', 'visitor-album', fileName)
    return { 'statusCode': 200 }
    
def updateAccessTimeStamp(faceId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    table.update_item(
        Key = {
            'faceId': faceId,
        },
        UpdateExpression = 'SET accessGranted =:x',
        ExpressionAttributeValues = {
            ':x': str(datetime.datetime.now())
        }
    )
    print('TIMESTAMP UPDATED')
def sendMsg(number,msg):
    client = boto3.client('sns')
    res = client.publish(PhoneNumber = number, Message = msg)
    print("MESSAGE SENT TO " + number)
    
def getRecord(faceId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    res = table.get_item(Key = {'faceId': faceId})
    return res['Item']
    
def setRecord(faceId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    it = {
        'faceId': faceId,
        'nickname': 'N/A',
        'phoneNumber': 'N/A',
        'verified' : False,
        'verification': False,
        'accessGranted' : 'N/A',
        'photos': [
            {
                'objectKey': faceId + '.jpg',
                'bucket': 'visitor-album',
                'createdTimestamp': str(datetime.datetime.now())
            }
        ]
    }
    table.put_item(Item = it)
    print("RECORD HAS BEEN SET")

def hasRecord(faceId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    res = table.get_item(Key = {'faceId' : faceId})
    if 'Item' in res:
        return True
    else: 
        return False

def setVerification(faceId, value = True):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    table.update_item(
        Key = {
            'faceId': faceId,
        },
        UpdateExpression = 'SET verification =:x',
        ExpressionAttributeValues = {
            ':x': value
        }
    )
    print('VERIFICATION HAS BEEN SET')

def isVerificationSent(visitor):
    return visitor['verification']

def addToCollection(cid, bucket, name, eid = "Unknown"):
    client = boto3.client('rekognition')
    res = client.index_faces(
        CollectionId = cid,
        Image={'S3Object':{'Bucket':bucket,'Name':name}},
        ExternalImageId= eid,
        MaxFaces=1,
        QualityFilter="AUTO",
        DetectionAttributes= ['ALL']    
    )
    print('FACE HAS BEEN ADDED TO COLLECTION')
    return res['FaceRecords']
    
def uploadToS3(src, bucket, name):
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        src,
        bucket, 
        name
    )
    print('IMAGE UPLOADED')
    
def isVerified(visitor):
    return visitor['verified']
    
def isAccessGranted(faceId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    res = table.get_item(Key = {'faceId': faceId})
    if 'Item' in res:
        lastAccess = res['Item']['accessGranted']
        if lastAccess != 'N/A':
            timeFormat = '%Y-%m-%d %H:%M:%S.%f'
            now = str(datetime.datetime.now())
            diff = datetime.datetime.strptime(now, timeFormat) - datetime.datetime.strptime(lastAccess, timeFormat)
            diff = diff.seconds
            return diff < 300
    return False

    
def getFacesFromStream():
    print("GET FACES FROM STREAM")
    res = []
    
    # get a frame of an instant from the stream
    kvs_client = boto3.client('kinesisvideo')
    kvs_data_pt = kvs_client.get_data_endpoint(
        StreamARN="arn:aws:kinesisvideo:us-east-1:781927886046:stream/KVS1/1584906673847", # kinesis stream arn
        APIName='GET_MEDIA'
    )
    
    end_pt = kvs_data_pt['DataEndpoint']
    kvs_video_client = boto3.client('kinesis-video-media', endpoint_url=end_pt, region_name='us-east-1') # provide your region
    kvs_stream = kvs_video_client.get_media(
        StreamARN='arn:aws:kinesisvideo:us-east-1:781927886046:stream/KVS1/1584906673847', # kinesis stream arn
        StartSelector={'StartSelectorType': 'NOW'} # to keep getting latest available chunk on the stream
    )
    
    with open('/tmp/stream.mkv', 'wb') as f:
        done = False
        streamBody = b''
        payload = kvs_stream['Payload']
        chunkSize = 1024 * 10
        
        # read upto 1MB to prevent timeout; some image is unnecessarily too big to read
        while not done and len(streamBody) < chunkSize * 100: 
            tmp = payload.read(chunkSize)
            if len(tmp) == 0:
                done = True
            else:
                streamBody += tmp
        
        if streamBody:
            f.write(streamBody)
            # use openCV to get a frame
            cap = cv2.VideoCapture('/tmp/stream.mkv')
            # use some logic to ensure the frame being read has the person, something like bounding box or median'th frame of the video etc
            ret, frame = cap.read()
            # load a file for bounding box
            face_detector_url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
            urlretrieve(face_detector_url,'/tmp/haarcascade_frontalface_default.xml')
            # Load cascade
            face_cascade = cv2.CascadeClassifier('/tmp/haarcascade_frontalface_default.xml')
            # Read the input image
            # Convert into grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces
            results = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for result in results:
                x,y,w,h = result
                row_ex, col_ex = h//5, w//5
                row1, row2 = max(0,y-row_ex), min(y+h+row_ex, frame.shape[0])
                col1, col2 = max(0,x-col_ex), min(x+w+col_ex, frame.shape[1])
                frame = frame[row1:row2,col1:col2]
                res.append(frame)
            
            cap.release()
                
    return res
    
def generateOTP(faceId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('passcodes')
    passcode = str(random.randint(100000,999999))
    ttl = datetime.datetime.now() + datetime.timedelta(minutes = 5)
    it = {
        'passcode' : passcode,
        'faceId' : faceId,
        'ttl' : int(ttl.timestamp())
    }
    table.put_item(Item = it)
    print('OTP HAS BEEN GENERATED')
    return passcode
    
def createMessage(sender: str, recipients: list, title: str, body: str=None, attachments: list=None) -> MIMEMultipart:
    multipart_content_subtype = 'mixed'
    msg = MIMEMultipart(multipart_content_subtype)
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    if body:
        part = MIMEText(body, 'html')
        msg.attach(part)
        
    for attachment in attachments or []:
        with open(attachment, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
            msg.attach(part)

    return msg
    
def sendEmail(sender: str, recipients: list, title: str, body: str=None, attachments: list=None) -> dict:
    msg = createMessage(sender, recipients, title, body, attachments)
    ses_client = boto3.client('ses')
    return ses_client.send_raw_email(
        Source=sender,
        Destinations=recipients,
        RawMessage={'Data': msg.as_string()}
    )

def downloadFromS3(bucket, key, path):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket).download_file(key, path)
    except botocore.exceptions.ClientError as e:
        print("DOWNLOADING FROM S3 FAILED DUE TO ", e.response['Error']['Code'])
        return False
    print("DOWNLOADED", key)
    return True

def sendVerification(faceId):
    # send a photo to ourselves and we will verify the person
    sender = 'hj2509@columbia.edu'
    recipients = [sender]
    title = 'Smart Authentication - Unknown Face Verification'
    body = '<html><head></head><body><p>                                                \
            This email was generated because of an enter attempt from                   \
            an unknown visitor.<br> The Smart-Door System requires                      \
            verification of the visitor. <br> If you recognize                          \
            the person and would like to grant access                                   \
            to the door, please click the link and fill out the form.                   \
            </p><a href="http://smartdoor.s3-website.us-east-1.amazonaws.com/?fid='
    body += faceId + '">http://smartdoor.s3-website.us-east-1.amazonaws.com/</a></body></html>'
    imgPath = '/tmp/' + faceId + '.jpg'
    
    # download the face of the unknown person from S3; if success, send an email
    if downloadFromS3('visitor-album', faceId + '.jpg', imgPath):
        attachments = [imgPath]
        res = sendEmail(sender, recipients, title, body, attachments)
        # now the face has been emailed as attachment, we are good to remove the face photo 
        os.remove(imgPath)
        print("VERIFICATION SENT")
        return True
    else:
        print(faceId + " DOES NOT EXIST IN S3! VERIFICATION WASNT SENT!!")
        return False
