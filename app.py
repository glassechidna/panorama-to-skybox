import logging
import os
import sys
import zipfile
from io import BytesIO

from PIL import Image
from flask import Flask, Response, flash, redirect, request, render_template, stream_with_context
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

FACE_SIZE = int(os.environ.get('FACE_SIZE') or '1024')

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

    def generate_zip():
        with BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "w") as zip:
                for face in CubeFace:
                    zip_buffer_face_offset = zip_buffer.tell()
                    populate_face(panorama_image, face_image, face)

                    with BytesIO() as image_bytes:
                        face_image.save(image_bytes, format=panorama_image.format)
                        image_bytes.seek(0)
                        face_filename = base_name + "_" + face.name.lower() + "." + extension
                        zip.writestr(face_filename, image_bytes.read(), zipfile.ZIP_STORED)

                    zip_buffer.seek(zip_buffer_face_offset)
                    yield zip_buffer.read()

                zip_buffer_offset = zip_buffer.tell()
                zip.close()
                zip_buffer.seek(zip_buffer_offset)
                yield zip_buffer.read()

    zip_name = base_name.replace('"', '\\"') + '_' + 'skybox.zip'
    return Response(stream_with_context(generate_zip()), mimetype='application/zip', headers={'Content-Disposition': 'attachment; filename="' + zip_name + '"'})
