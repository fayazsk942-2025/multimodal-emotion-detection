from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout as auth_logout
import numpy as np
import joblib
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm


from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory, models

from django.contrib import messages

import joblib
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import UserImageModel
from .forms import UserImageForm
import numpy as np
import joblib
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import UserImageForm
from sklearn.metrics import precision_recall_curve
from django.shortcuts import render
from django.core.mail import EmailMessage

from django.shortcuts import render
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
from tensorflow import keras
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory, models
from django.contrib import messages
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import numpy as np
import joblib
from . import forms
from .models import UserImageModel

import cv2
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['figure.figsize'] = (12, 12)
mpl.rcParams['axes.grid'] = False
import time
from  joblib import load



def home(request):
    return render(request, 'users/home.html')

@login_required(login_url='users-register')


def index(request):
    return render(request, 'app/index.html')

class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality

class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        # Ensure that the user has a profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=profile)

    return render(request, 'users/profile.html', {'user_fofrm': user_form, 'profile_form': profile_form})

from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.mail import send_mail
from .forms import AudioForm
from .models import AudioPrediction
import numpy as np
import librosa
from tensorflow.keras.models import load_model
import os


def extract_features(file_path):
    audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    mfccs_processed = np.mean(mfccs.T, axis=0)
    return mfccs_processed


def send_audio_sad_email(prediction):
    send_mail(
        subject="🚨 Audio Emotion Alert: Sadness Detected",
        message=f"""
Audio Emotion Alert 🚨

Detected Emotion: {prediction}

Sad emotion detected from audio input.
Please consider immediate attention or support.
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['agalyaspiro25@gmail.com'],
        fail_silently=False,
    )


def model(request):
    if request.method == 'POST':
        form = AudioForm(request.POST, request.FILES)
        if form.is_valid():

            audio_file = request.FILES['audio_file']
            file_name = default_storage.save(audio_file.name, audio_file)
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            # Feature extraction
            features = extract_features(file_path)
            features = np.expand_dims(features, axis=0)
            features = np.expand_dims(features, axis=-1)

            # Load model
            audio_model = load_model('users/human.h5', compile=False)

            # Prediction
            predicted_class = audio_model.predict(features)
            predicted_label = np.argmax(predicted_class)

            class_mapping = {
                0: 'Angry',
                1: 'Fear',
                2: 'Happy',
                3: 'Sad',
                4: 'Unknown',
            }

            prediction = class_mapping.get(predicted_label, 'Unlabelled')

            # Save to DB
            audio_prediction = AudioPrediction(
                audio_file=audio_file,
                prediction=prediction
            )
            audio_prediction.save()

            # 📧 SEND EMAIL ONLY IF SAD
            if prediction == 'Sad':
                print("📧 SAD AUDIO DETECTED → EMAIL SENT")
                send_audio_sad_email(prediction)
            else:
                print("❌ NO EMAIL → Emotion:", prediction)

            return render(
                request,
                'app/output.html',
                {
                    'prediction': prediction,
                    'audio_file': audio_prediction
                }
            )

        return render(request, 'app/Deploy_8.html', {'form': form})

    return render(request, 'app/Deploy_8.html')

def model_db(request):
    
    models = AudioPrediction.objects.all()
    return render(request, 'app/model_db.html', {'models':models})




def logout_view(request):  
    auth_logout(request)
    return redirect('/')



from django.shortcuts import render
from .models import Profile

def profile_list(request):

    profiles = Profile.objects.all()

    return render(request, 'app/profile_list.html', {'profiles': profiles})

            
def send_text_emotion_email(emotion, text):
    send_mail(
        subject="🚨 Sad Emotion Detected (Text Analysis)",
        message=f"""
TEXT EMOTION ALERT 🚨

Detected Emotion: {emotion}

User Input:
{text}
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['agalyaspiro25@gmail.com'],
        fail_silently=False,
    )

from django.shortcuts import render
from .models import Prediction
from transformers import BertTokenizer, BertForSequenceClassification
import torch


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

bert_model = BertForSequenceClassification.from_pretrained(
    'users/saved_emotion_model'
)
bert_model.eval()


def Deploy(request):
    if request.method == "POST":

        text_input = request.POST.get("message", "").strip()

        if not text_input:
            return render(request, "Deploy.html", {
                "error": "Please enter text"
            })

        # Tokenize
        inputs = tokenizer(
            text_input,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = bert_model(**inputs)

        predicted_id = torch.argmax(outputs.logits, dim=1).item()

        label_map = {
            0: "anger",
            1: "disgust",
            2: "fear",
            3: "joy",
            4: "neutral",
            5: "sadness",
            6: "shame",
            7: "surprise"
        }

        prediction = label_map.get(predicted_id, "unknown")

        # ✅ Save to DB
        Prediction.objects.create(
            input_text=text_input,
            output_label=prediction
        )

        # 📧 SEND EMAIL ONLY IF SADNESS
        if prediction == "sadness":
            try:
                send_text_emotion_email(prediction, text_input)
                print("✅ SAD EMAIL SENT")
            except Exception as e:
                print("❌ EMAIL ERROR:", e)

        return render(
            request,
            "app/output1.html",
            {"prediction_text": prediction}
        )

    return render(request, "app/Deploy.html")

from django.shortcuts import render
from .models import Prediction

def PredictionDB(request):
    # Get all saved predictions
    all_predictions = Prediction.objects.all().order_by('-id')  # latest first

    return render(request, "app/prediction_db.html", {
        "predictions": all_predictions
    })

import cv2
from deepface import DeepFace
import numpy as np
from tensorflow.keras.models import model_from_json
import copy
from .models import DetectedEmotion   # ✅ ADD


def emotions(request):
    if request.method == 'POST':
        
        face_classifier = cv2.CascadeClassifier("users/facerec/models/haarcascade_frontalface_default.xml")

        model_json_file = "H:emosense/users/facerec/models/model.json"
        model_weights_file = "users/facerec/models/Latest_Model.h5"
        with open("users/facerec/models/model.json", "r") as json_file:
            loaded_model_json = json_file.read()
            classifier = model_from_json(loaded_model_json)
            classifier.load_weights(model_weights_file)



        cap = cv2.VideoCapture(0)


        while True:

            ret, frame = cap.read()
            img = copy.deepcopy(frame)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                fc = gray[y:y+h, x:x+w]

                roi = cv2.resize(fc, (48,48))
                pred = classifier.predict(roi[np.newaxis, :, :, np.newaxis])
                text_idx=np.argmax(pred)
                text_list = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
                if text_idx == 0:
                    text= text_list[0]
                    print('Angry')
                if text_idx == 1:
                    text= text_list[1]
                    print('Disgust')
                elif text_idx == 2:
                    text= text_list[2]
                    print('Fear')
                elif text_idx == 3:
                    text= text_list[3]
                    print('Happy')
                elif text_idx == 4:
                    text= text_list[4]
                    print('Neutral')
                elif text_idx == 5:
                    text= text_list[5]
                    print('Sad')
                elif text_idx == 6:
                    text= text_list[6]
                    print('Surprise')
                cv2.putText(img, text, (x, y-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                img = cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)


            cv2.imshow("frame", img)
            key = cv2.waitKey(1) & 0xFF
            if key== ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        return render(request, 'users/emotions.html', {"PREDICTION":cv2.imshow('img', img)})
    
    else:
        return render(request, 'users/emotions.html')

    
from .models import DetectedEmotion

def emotion_history(request):
    emotions = DetectedEmotion.objects.order_by('-created_at')
    return render(request, 'users/emotion_history.html', {'emotions': emotions})




from django.shortcuts import render
from django.http import JsonResponse
# import random
# import json
import numpy as np
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer
#from .models import Response, models
from Chatbot.processor import chatbot_response
# Remove the comments to download additional nltk packages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@require_POST
@csrf_exempt
def chatbot_response_view(request):
    if request.method == 'POST':
        the_question = request.POST.get('question', '')

        response = chatbot_response(the_question)
        print(response)

        return JsonResponse({"response": response})
    else:
        
        return JsonResponse({"message": "This endpoint only accepts POST requests."})
 
def bott(request):
    return render(request, 'app/bott.html')

