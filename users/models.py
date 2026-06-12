from django.db import models
from django.contrib.auth.models import User
from PIL import Image


# Extending User Model Using a One-To-One Link
from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

    def __str__(self):
        return self.user.username

    # resizing images
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)









from django.db import models
class UserImageModel(models.Model):
    image = models.ImageField(upload_to = 'predict/')
    label = models.CharField(max_length=255,default='data')

    def __str__(self):
        return str(self.image)


# models.py
from django.db import models

class AudioPrediction(models.Model):
    audio_file = models.FileField(upload_to='audio_files/')
    prediction = models.CharField(max_length=50)
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.prediction
class Prediction(models.Model):
    input_text = models.TextField()
    output_label = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.input_text[:50]} - {self.output_label}"
    



class DetectedEmotion(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    emotion = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.emotion} at {self.timestamp}"
from django.db import models

class Detected(models.Model):
    """Stores detected criminal names (without weapon)"""
    name = models.CharField(max_length=100)
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class EmotionDetection(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    emotion = models.CharField(max_length=100)
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.emotion} at {self.detected_at}"
    
from django.db import models

class Prediction(models.Model):
    input_text = models.TextField()
    output_label = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.input_text[:20]}... -> {self.output_label}"


# models.py
from django.db import models

class DetectedEmotion(models.Model):
    emotion = models.CharField(max_length=50)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

