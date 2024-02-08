from flask import Flask, request, send_file, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import urllib.parse
import random


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"mp3", "mp4", "ogg", "wav", "avi"}
UPLOADS_FOLDER = "./uploads"


@app.route("/", methods=["GET"])
def get_songs():
    loaded_song_names = []

    if os.path.exists(UPLOADS_FOLDER):
        loaded_song_names.extend(os.listdir(UPLOADS_FOLDER))

    else:
        os.mkdir(UPLOADS_FOLDER)

    loaded_song_paths = list()
    for song in loaded_song_names:
        loaded_song_paths.append(request.base_url + "/uploads/" + urllib.parse.quote(song))

    # randomize
    random.shuffle(loaded_song_paths)

    return render_template("song_list.html", title="Found music", songs=loaded_song_paths)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["GET", "POST"])
def upload_songs():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template("upload_status.html", title="Chyba!", content="Soubor nenalezen!")

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return render_template("upload_status.html", title="Chyba!", content="Soubor nebyl vybrán!")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOADS_FOLDER, filename))
            return render_template("upload_status.html", title="Úspěch!", content="Soubor byl úspěšně nahrán")
            
    
    return '''
    <!doctype html>
    <title>Nový soubor</title>
    <a href="../">
        <button>
            Zpět
        </button>
    </a>
    <hr>
    <h1>Nahrát nový soubor</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/download_file/<path:filename>', methods=["GET"])
def download_file(filename):

    return send_file(os.path.join(UPLOADS_FOLDER, filename), as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4650)