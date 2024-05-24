import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
from flask import Flask, request, redirect, url_for, render_template


app = Flask(__name__,static_folder='C:/uploads')


UPLOAD_FOLDER = 'E:/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Замените на ваши ключи Google reCAPTCHA
SECRET_KEY = "6LeJFtApAAAAAA9e7wBn0hC2mJo2NIOM5kDZ8MBN"
SITE_KEY = "6LeJFtApAAAAACGMGgam1GpQGBrEoowXhGEOaJIK"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Проверка Google reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verify_recaptcha(recaptcha_response):
            return "Ошибка проверки капчи"

        file = request.files['image']
        angle = int(request.form['angle'])

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        image = Image.open(file_path)
        rotated_image = image.rotate(angle)

        # Создание гистограмм для изображений
        original_hist = image.histogram()
        rotated_hist = rotated_image.histogram()

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(original_hist, color='b')
        plt.title('Original Image Histogram')
        plt.xlabel('Интенсивность пикселей')
        plt.ylabel('Частота')
        plt.subplot(1, 2, 2)
        plt.plot(rotated_hist, color='r')
        plt.title('Rotated Image Histogram')
        plt.xlabel('Интенсивность пикселей')
        plt.ylabel('Частота')

        rotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'rotated_image.png')
        histograms_path = os.path.join(app.config['UPLOAD_FOLDER'], 'histograms.png')
        plt.savefig(histograms_path)
        rotated_image.save(rotated_image_path)

        return render_template('index.html',
                               original_image=file.filename,
                               rotated_image='rotated_image.png',
                               histograms='histograms.png')

    return render_template('index.html', site_key=SITE_KEY)

def verify_recaptcha(recaptcha_response):
    payload = {
        'secret': SECRET_KEY,
        'response': recaptcha_response
    }
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    result = response.json()
    return result['success']

if __name__ == '__main__':
    app.run(debug=True)