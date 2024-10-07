from ninja import NinjaAPI, Schema, ModelSchema, Query, FilterSchema
from dotenv import load_dotenv
from ninja.security import django_auth
import os
import httpx

from django.contrib.auth import get_user_model
from SignInSystem.models import CustomUser
from asgiref.sync import sync_to_async


from .models import AudioDatabase

import aiohttp

import boto3

from botocore.exceptions import NoCredentialsError, ClientError




load_dotenv()
piperkey = os.environ['PIPER_KEY']

AudioAPI = NinjaAPI(urls_namespace='AudioAPI')


AWS_ACCESS_KEY_ID=os.environ['AWS_ACCESS_KEY_ID']
AWS_ACCESS_SECRET_KEY_ID=os.environ['AWS_ACCESS_SECRET_KEY_ID']
AWS_STORAGE_BUCKET_NAME=os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_LOCATION=os.environ['AWS_S3_REGION_LOCATION']

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_ACCESS_SECRET_KEY_ID,
                  region_name=AWS_S3_REGION_LOCATION
                  )

#class UserSchema(ModelSchema):
#     class Meta:
#          model = User
#          fields = ['folder_id', 'username']

#class UserFolderExistsFilter(FilterSchema):
#     def exists(self, condition1, condition2):
#        # Filter the model queryset based on your condition
#          return User.objects.filter(condition1, condition2).exists()
#
#
class S3FileInfo_psUrl(Schema):
     file_path : str
     bucket_name : str
     name_file : str


class TtsCreateSchema(Schema):
     input_text : str
     name_file : str
     voice_model : str
     folder_id : str
     username : str

class GetUserLibrarySchema(Schema):
    username : str
    folder_id : str

# need an asycnhronous function within the async api
@sync_to_async
def get_users(username, folder_id):
    return list(
        CustomUser.objects.filter(username=username, folder_id=folder_id)
    )

#ASYNC DEFAULT PYTHON VERSION THAT BROKE
#@sync_to_async
#def log_api_response_200(username, folder_id, name_file, voice_model, input_text, response):
#     return (AudioDatabase.objects.create(
#               username=username, # not sure why this is username_id in table when model says username
#               folder_id=folder_id,
#               request_textdata=input_text,
#               bucket_name=response.json().get("bucket_name"),
#               response_file_location=response.json().get("file_path"),
#               systemfile_name=response.json().get("name_of_file"),
#               response_time_to_complete=response.json().get("execution_time"),
#               userfile_name=name_file,
#               voice=voice_model,
#               length_of_audio_seconds=response.json().get("lengthOfFileSeconds"),
#               file_sizeMB=response.json().get("file_sizeMB")
#               ))

# aiohttp VERSION
@sync_to_async
def log_api_response_200(username, folder_id, name_file, voice_model, input_text, response):
     return (AudioDatabase.objects.create(
               username=username, # not sure why this is username_id in table when model says username
               folder_id=folder_id,
               request_textdata=input_text,
               bucket_name=response.get("bucket_name"),
               response_file_location=response.get("file_path"),
               systemfile_name=response.get("name_of_file"),
               response_time_to_complete=response.get("execution_time"),
               userfile_name=name_file,
               voice=voice_model,
               length_of_audio_seconds=response.get("lengthOfFileSeconds"),
               file_sizeMB=response.get("file_sizeMB")
               ))





@AudioAPI.post("/ttsrequest")
async def ttsrequest(request, ttsreq: TtsCreateSchema):# filters: UserFolderExistsFilter = Query(...)):
     input_text  = ttsreq.input_text
     name_file  = ttsreq.name_file
     voice_model  = ttsreq.voice_model

     # Extract user information
     username = ttsreq.username
     folder_id = ttsreq.folder_id

     checkCredentials= 0

     #credentials check if username and folder_id match
     checkCredentials = await get_users(username, folder_id)
     # user must exist with match folder_id and username
     if len(checkCredentials) < 1:
          return f"error: invalid credentials"

     api_data = {
          'input_text': input_text,
          'model_name': voice_model,
          'userid': folder_id,
          'name_file': name_file,
          'key': piperkey
     }

     try:
          #async with httpx.AsyncClient() as client: stopped working for no apparent reason saying pipe broke
          async with aiohttp.ClientSession() as session:
               async with session.post('http://127.0.0.1:7000/ttsapi/ttsCreate', json=api_data) as response:
               #response = await client.post('http://127.0.0.1:7000/ttsapi/ttsCreate', json=api_data)

                    if response.status == 200:
                    # Handle success

                         #function to save the data here
                         json_response = await response.json()
                         audiolog = await log_api_response_200(username, folder_id,name_file, voice_model, input_text, json_response)

                         return {"message": "Request processed successfully", "status": f"{response.status}"}
                    else:
                         # Handle failure
                         return {"error": "Failed to process request",  "status": f"{response.status}"}
     except:
          return AudioAPI.create_response(
          request,
          {"message": "could not process asynchrnous api"},
          status=400,
     )


@AudioAPI.get("/getuserlibrarydata")
def getuserlibrarydata(request, userinfo: GetUserLibrarySchema):
     audio_library_data = AudioDatabase.objects.filter(username=userinfo.username, folder_id=userinfo.folder_id, deletedTF=0)
     #audio_library_data_JSON = 0
     # MUST USE NINJA TO SERIALIZE THE MODEL DATA
     return audio_library_data#_JSON

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_ACCESS_SECRET_KEY_ID,
                  region_name=AWS_S3_REGION_LOCATION
                  )

@AudioAPI.get("/s3userrequestfileurl")
def s3userrequestfileurl(request, file_path : str, bucket_name : str, name_file : str):
     try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_path},
            ExpiresIn=(2*60*60) #2 hours
        )
        return url
     except ClientError as e:
          print(f"Error generating pre-signed URL: {e}")
          return None



@AudioAPI.get("/getaudiolibrarydatamodel")
def get_audios_by_username(request, username: str, folder_id: str):
    audios = AudioDatabase.objects.filter(username=username, folder_id=folder_id)
    return [
        {
          "id": audio.id,
          "username": audio.username,
          "folder_id": audio.folder_id,
          "timestamp": audio.timestamp,
          "request_textdata": audio.request_textdata,
          "bucket_name": audio.bucket_name,
          "response_file_location": audio.response_file_location,
          "response_time_to_complete": audio.response_time_to_complete,
          "systemfile_name": audio.systemfile_name,
          "userfile_name": audio.userfile_name,
          "voice": audio.voice,
          "deletedTF": audio.deletedTF,
          "length_of_audio_seconds": audio.length_of_audio_seconds,
          "file_sizeMB": audio.file_sizeMB,
          "public_post" : audio.public_post,
          "friends_view_post" : audio.friends_view_post
        }
        for audio in audios
    ]

@AudioAPI.delete("/deleteaudiofiles3")
def deleteaudiofiles3(request, file_path: str, bucket_name: str, audioId: str):
     try:
          # Delete the file from the S3 bucket
          audio_file = AudioDatabase.objects.get(id=audioId)
          audio_file.delete()
          # need to change both front and backend to post and alter json to not delete data
          #audio_file.deletedTF = 1
          #audio_file.save()
          s3.delete_object(Bucket=bucket_name, Key=file_path)
          return {"message": "File deleted successfully."}
     except ClientError as e:
          return {"error": f"Failed to delete file: {e.response['Error']['Message']}"}, 400
     except NoCredentialsError:
          return {"error": "Credentials not available."}, 400


demos_dict = {
          "Kenny (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "kenny demo_usaKenny.wav", },
          "Jenny (Ireland)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "kenny jenny demo_irishGirl.wav", },
          "Stan (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "stan demo_usaStan (1).wav", },
          "Eric (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "Ericdemov_usaEric.wav", },
          "Melanie (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "melanie demo_usaMel.wav", },
          "Sarah (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "sarah demo_usaSarah.wav", },
          "Kyle (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "kyle demo_usaKyle.wav", },
          "Alba (Scotland)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "alba demo_scotGirl.wav", },
          "Shelly (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "shelly demo_usaShelly.wav", },
          "Anne (USA)" : {"bucket_name": "podgeaudioapp/","folder_id": "demos/", "filename": "anne demo_usaAnne.wav", }
          }
@AudioAPI.get("/fetchaudiosampleinfo")
def fetchaudiosampleinfo(request):
     return demos_dict

