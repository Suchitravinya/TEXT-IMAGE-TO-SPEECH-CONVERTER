from flask import Flask, render_template, request, send_from_directory
import os
import pytesseract as tess
from PIL import Image
from googletrans import Translator
from gtts import gTTS
import pythoncom

app = Flask(__name__)
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    pythoncom.CoInitialize()  # Initialize COM for multi-threaded environments
    folder_path = 'uploads'
    if 'user_text' in request.form and request.form['user_text'].strip() != '':
        user_text = request.form['user_text']
        selected_language = request.form.get('language')
        translator = Translator()
        translated_text = translator.translate(user_text, src='en', dest=selected_language).text
        if selected_language == 'kn':
            tts = gTTS(text=translated_text, lang='kn')
        elif selected_language == 'hi':
            tts = gTTS(text=translated_text, lang='hi')
        else:
            tts = gTTS(text=translated_text, lang='en')
        audio_path = 'uploads/audio_speech.mp3'
        tts.save(audio_path)
        return render_template('result.html', text=translated_text, selected_language=selected_language, audio_path=audio_path)
    elif 'image' in request.files:
        image_file = request.files['image']
        image_path = os.path.join('uploads', image_file.filename)
        image_file.save(image_path)
        img = Image.open(image_path)
        extracted_text = tess.image_to_string(img)
        selected_language = request.form.get('language')
        translator = Translator()
        translated_text = translator.translate(extracted_text, src='en', dest=selected_language).text
        translated_text = translator.translate(extracted_text, src='en', dest=selected_language).text
        
        # Generate the audio file in the selected language
        if selected_language in ['kn', 'hi', 'ta', 'es', 'fr']:
            tts = gTTS(text=translated_text, lang=selected_language)
        else:
            tts = gTTS(text=translated_text, lang='en')

        audio_path = 'uploads/audio_speech.mp3'
        tts.save(audio_path)
        os.remove(image_path)
        return render_template('result.html', text=translated_text, selected_language=selected_language, audio_path=audio_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
