from django.contrib import admin
from .models import UserImageModel
from .models import Profile

admin.site.register(UserImageModel)
admin.site.register(Profile)
