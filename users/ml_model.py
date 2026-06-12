from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "fayazsk942/fayaz-emotion-bert"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()


def predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()

    return prediction

from django.shortcuts import render
from django.http import JsonResponse
from .ml_model import predict

def predict_emotion(request):
    text = request.GET.get("text")

    if not text:
        return JsonResponse({"error": "No text provided"})

    result = predict(text)

    return JsonResponse({
        "prediction": result
    })