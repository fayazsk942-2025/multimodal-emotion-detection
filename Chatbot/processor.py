import os
import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from googletrans import Translator
from gtts import gTTS
from pygame import mixer
import google.generativeai as genai

# Initialize lemmatizer and environment
lemmatizer = WordNetLemmatizer()
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# 🔑 Configure Gemini API key
genai.configure(api_key="AIzaSyCmJ7JrSjaKIx2OMP_t3mmyH2BHsSyIPk8")
model = genai.GenerativeModel("gemini-2.5-flash")  # You can use gemini-1.5-pro for more accuracy

# Load intents (existing)
intents = json.loads(open('Chatbot/intents.json', encoding='utf-8').read())

# Initialize translator
translator = Translator()

def clean_up_sentence(sentence, source_lang='en', target_lang='en'):
    """Translates and tokenizes the input text"""
    translation = translator.translate(sentence, src=source_lang, dest=target_lang).text
    sentence_words = nltk.word_tokenize(translation)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    print("This is the input text ", sentence_words)
    return sentence_words


def chatbot_response(msg, source_lang='en', target_lang='en', save_path="Responses/response.mp3"):
    """Generates response using Gemini instead of local model"""
    try:
        # 🌐 Send to Gemini
        prompt = f"""
    You are an empathetic emotion-support chatbot and micro-therapy assistant.

    Your role:
    - Greet the user politely (e.g., "Hi", "Hello, how are you feeling today?")
    - Understand the user's emotional state from their message
    - Respond in a calm, friendly, warm, and non-judgmental tone

    If the user expresses negative emotions (sad, stressed, anxious, angry, lonely, low mood):
    - Acknowledge and validate their feelings empathetically
    - Provide gentle micro-therapy suggestions such as:
    - simple breathing exercises
    - grounding techniques
    - positive reframing
    - short self-care activities
    - motivational or reassuring words

    🎵 Music recommendation rules (VERY IMPORTANT):
    - Do NOT suggest songs unless the user explicitly asks for music or songs
    - If the user asks for songs:
    - Detect the language mentioned by the user
    - Recommend songs ONLY in that language
        - If user says "Tamil" → suggest Tamil songs
        - If user says "Telugu" → suggest Telugu songs
        - If user says "Hindi" → suggest Hindi songs
        - If user says "English" → suggest English songs
        - If no language is mentioned → ask politely which language they prefer
    - Suggest only 3–5 songs
    - Mention clearly:
    - Song name
    - Movie name (if applicable)
    - Choose songs suitable for:
    - relaxation
    - emotional healing
    - motivation
    - calm mood

    Safety rules:
    - Keep responses simple, friendly, and human-like
    - Do NOT act as a medical professional
    - Do NOT give diagnosis or medication advice
    - Avoid triggering or harmful content
    - Encourage positivity, emotional balance, and self-care

    User message: "{msg}"
"""

        
        response = model.generate_content(prompt)
        result = response.text.strip()

        # Translate output if needed
        translation = translator.translate(result, src=source_lang, dest=target_lang).text

        # 🔊 Text to speech
        tts = gTTS(text=translation, lang=target_lang)
        tts.save(save_path)
        mixer.init()
        sound = mixer.Sound(save_path)
        sound.play()

        return translation

    except Exception as e:
        print("Error in chatbot_response:", e)
        return "Sorry, I couldn't process your question. Please try again."


# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = chatbot_response(user_input)
        print("Bot:", response)
