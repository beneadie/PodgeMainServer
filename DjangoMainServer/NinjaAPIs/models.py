from django.db import models

from SignInSystem.models import CustomUser

class AudioDatabase(models.Model):
    #username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=255) # for some reason it comes up as username_id in table
    folder_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    request_textdata = models.TextField()
    bucket_name = models.TextField(default="podgeaudioapp", max_length=1000)
    response_file_location = models.TextField(max_length=1000)
    response_time_to_complete = models.FloatField(default=0.0)
    systemfile_name = models.CharField(max_length=255)
    userfile_name = models.CharField(max_length=255)
    voice = models.CharField(max_length=255)
    deletedTF = models.BooleanField(default=False)
    length_of_audio_seconds = models.IntegerField(default=0)
    file_sizeMB = models.FloatField(default=0.0)

    public_post = models.BooleanField(default=False)
    friends_view_post = models.BooleanField(default=False)


#http://127.0.0.1:8000/apis/manageAudio/getaudiolibrarydatamodel?username=stella3&folder_id=142cd733-0a1b-481a-9cba-c085e8d97ef3
#http://127.0.0.1:8000/apis/manageAudio/getaudiolibarydatamodel?username=stella3&folder_id=142cd733-0a1b-481a-9cba-c085e8d97ef3
