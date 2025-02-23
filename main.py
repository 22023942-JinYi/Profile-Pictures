import cv2
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import shutil
import webbrowser
from threading import Thread
import time  # For simulating progress updates
import zipfile
import json
import tempfile

app = Flask(__name__)


#Not suitable for website as no directory or storage on internet or .exe
'''UPLOAD_FOLDER = os.path.join(script_path, 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(script_path, 'output')
WRONG_FOLDER = os.path.join(OUTPUT_FOLDER, 'unacceptable')'''

def create_temp_dirs():
    global UPLOAD_FOLDER, WRONG_FOLDER, OUTPUT_FOLDER, ZIP_FOLDER
    UPLOAD_FOLDER = tempfile.TemporaryDirectory()
    OUTPUT_FOLDER = tempfile.TemporaryDirectory()
    WRONG_FOLDER = os.path.join(OUTPUT_FOLDER.name, "unacceptable")
    ZIP_FOLDER = tempfile.TemporaryDirectory()

    os.makedirs(WRONG_FOLDER)

create_temp_dirs()

def deletefiles():

    UPLOAD_FOLDER.cleanup()
    OUTPUT_FOLDER.cleanup()
    ZIP_FOLDER.cleanup()

    create_temp_dirs()


def cropfaces():
    global progress
    global zip_filepath
    global filename
    global message
    global selected_dimensions 
    output = ''
    message = ''
    progress = 0
    cascade_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'haarcascade_frontalface_alt2.xml')
    face_cascade = cv2.CascadeClassifier(cascade_file_path)

    for inputfile in os.listdir(UPLOAD_FOLDER.name):
        if os.path.isdir(os.path.join(UPLOAD_FOLDER.name, inputfile)):
            uploadfolder = os.path.join(UPLOAD_FOLDER.name, inputfile)
        else:
            uploadfolder = UPLOAD_FOLDER.name

    files = os.listdir(uploadfolder)
    total_files = len(files)

    if total_files == 0:
        return

    each_file_progress = 1/total_files * 100

    width, height = map(int, selected_dimensions.split('x'))

    for i, file in enumerate(files):
        message = f'Cropping {file}'
        filepath = os.path.join(uploadfolder, file)
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            img_height, img_width, _ = img.shape

            size_face_height = (y + h) - y

            if img_height > img_width:
                size = img_width
            else:
                size = img_height

            gaps = size - size_face_height
            dividegaps = int(gaps / 2)

            startx = x - dividegaps
            endx = x + w + dividegaps

            if startx < 0:
                startx = 0

            starty = y - dividegaps
            endy = y + h + dividegaps

            if starty < 0:
                starty = 0
            elif starty > 100:
                starty = y - dividegaps - 100
                endy = y + h + dividegaps + 100

            if endx > img_width:
                endx = img_width
            if endy > img_height:
                endy = img_height

            if (endx - startx) > (endy - starty):
                gap = endx - startx -  endy 
                dividegaps = int(gap / 2)
                if starty >= dividegaps:
                    endy += dividegaps
                    starty -= dividegaps
                else:
                    starty = 0
                    endy += gap

            elif (endx - startx) < (endy - starty):
                gap = endy - starty - endx
                dividegaps = int(gap / 2)
                if startx >= dividegaps:
                    endx += gap
                    startx -= gap
                else:
                    startx = 0
                    endx += gap

            face = img[starty:endy, startx:endx]

            face_height, face_width, _ = face.shape
            print("Face size:", face_width, "x", face_height, "pixels")

            txtfile = open(os.path.join(OUTPUT_FOLDER.name, '1.unacceptable.txt'), 'w')

            if face_width != face_height:
                output += f'{file}\nFace size: {face_width} x {face_height} pixels\n'
                print(WRONG_FOLDER)
                cv2.imwrite(os.path.join(WRONG_FOLDER, file), img)
            else:
                face = cv2.resize(face, (width, height))
                cv2.imwrite(os.path.join(OUTPUT_FOLDER.name, file), face)
            
            txtfile.write(output)
            txtfile.close()

        progress += int(each_file_progress)
        print(progress)
        time.sleep(0.05)  # Simulate some delay for progress

    message = 'Zipping File'
    filename = 'download'
    zip_filepath = os.path.join(ZIP_FOLDER.name, 'download.zip')

    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(OUTPUT_FOLDER.name):
            for file in files:
                filepath = os.path.join(root, file)
                print(filepath)
                print(os.path.relpath(filepath, OUTPUT_FOLDER.name))
                zip_file.write(filepath, os.path.relpath(filepath, OUTPUT_FOLDER.name))

    progress = 100
    time.sleep(1)

@app.route('/')
def index():
    deletefiles()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400

    files = request.files.getlist('files')
    for file in files:
        if file:
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER.name, filename))

    return jsonify({'message': 'Files uploaded successfully'}), 200

@app.route('/reorder')
def reorder():
    files = os.listdir(UPLOAD_FOLDER.name)
    return render_template('reorder.html', files=files)

@app.route('/uploads/<filename>')
def serve_image(filename):
    UPLOAD_FOLDER_PATH = UPLOAD_FOLDER.name
    return send_from_directory(UPLOAD_FOLDER_PATH, filename)

@app.route('/submit', methods=['POST'])
def save_order():
    global selected_dimensions 

    data = request.json
    files = data.get('files')
    selected_dimensions = data.get('dimensions')
    Thread(target=cropfaces).start()
    return jsonify({'message': 'Order saved successfully'}), 200

@app.route('/progress', methods=['GET'])
def check_progress():
    global progress
    print(progress)
    return json.dumps({'progress': progress, 'message': message})

@app.route('/download', methods=['POST'])
def download():
    global zip_filepath
    global filename

    _, extension = os.path.splitext(zip_filepath)
    custom_filename = f"{filename}{extension}"

    return send_file(zip_filepath, as_attachment=True, download_name=custom_filename)


def open_webbrowser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == '__main__':
    open_webbrowser()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
