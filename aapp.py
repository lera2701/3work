import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__, static_folder='E:/uploads')

UPLOAD_FOLDER = 'E:/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Замените на ваши ключи Google reCAPTCHA
SECRET_KEY = "6Lfeh-EpAAAAAJLTw3wi2XvzoiDtud6K8LMbCZfi"
SITE_KEY = "6Lfeh-EpAAAAAJLTw3wi2XvzoiDtud6K8LMbCZfi"

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
        original_image_array = np.array(image)
        rotated_image_array = np.array(rotated_image)

        original_color_distribution = np.zeros(256)
        rotated_color_distribution = np.zeros(256)

        for row in original_image_array:
            for pixel in row:
                original_color_distribution[pixel] += 1

        for row in rotated_image_array:
            for pixel in row:
                rotated_color_distribution[pixel] += 1

        max_frequency = 10000

        original_color_distribution = original_color_distribution * (max_frequency / np.max(original_color_distribution))
        rotated_color_distribution = rotated_color_distribution * (max_frequency / np.max(rotated_color_distribution))

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.bar(range(256), original_color_distribution, color='b', alpha=0.7)
        plt.title('Распределение цветов исходного изображения')
        plt.xlabel('Значение пикселя')
        plt.ylabel('Частота')
        plt.ylim(0, max_frequency)
        plt.subplot(1, 2, 2)
        plt.bar(range(256), rotated_color_distribution, color='r', alpha=0.7)
        plt.title('Распределение цветов повернутого изображения')
        plt.xlabel('Значение пикселя')
        plt.ylabel('Частота')
        plt.ylim(0, max_frequency)

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