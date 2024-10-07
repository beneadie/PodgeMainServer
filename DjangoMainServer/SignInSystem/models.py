from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

"""
Used the imported default 'AbstractUser' model from django and added custom fields
"""
class CustomUser(AbstractUser):
     folder_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)

     verified_tf = models.BooleanField(default=False)
     paying_user = models.BooleanField(default=False)
     was_once_paying_user = models.BooleanField(default=False)
