import logging
import os
import sys
import zipfile
from io import BytesIO

from PIL import Image
from flask import Flask, Response, abort, flash, redirect, request, render_template, send_file
from flask_cors import CORS

from panorama import populate_face, CubeFace

try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except:
    pass

SECRET_KEY = os.environ.get('SECRET_KEY') or 'N0t@ALL_$ecretk3y:('

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

cors = CORS(app)

if 'DYNO' in os.environ:
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

FACE_SIZE = int(os.environ.get('FACE_SIZE') or '512')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect('/')

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect('/')

    try:
        components = file.filename.rsplit('.', 2)
        base_name = components[0]
        extension = components[1]

        panorama_image = Image.open(request.files['file'].stream)
    except Exception:
        flash('Uploaded file was not a valid image')
        return redirect('/')

    face_image = Image.new('RGB', (FACE_SIZE, FACE_SIZE), 'black')

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip:
        for face in CubeFace:
            populate_face(panorama_image, face_image, face)
            face_filename = base_name + "_" + face.name.lower() + "." + extension

            with BytesIO() as image_bytes:
                face_image.save(image_bytes, format=panorama_image.format)
                image_bytes.seek(0)
                zip.writestr(face_filename, image_bytes.read(), zipfile.ZIP_STORED)

        zip_name = base_name + '_' + 'skybox.zip'

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, attachment_filename=zip_name, mimetype='application/zip')
