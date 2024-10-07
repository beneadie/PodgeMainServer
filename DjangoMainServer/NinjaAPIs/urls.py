from django.contrib import admin
from django.urls import path, re_path, include

from .ContentProcessingNinja import TextAPI
from .AudioFileManagementNinja import AudioAPI



urlpatterns = [
    path("cpapi/", TextAPI.urls),
    path("manageAudio/", AudioAPI.urls)
]
