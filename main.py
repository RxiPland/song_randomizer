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
        loaded_song_paths.append(request.base_url + "uploads/" + urllib.parse.quote(song))

    # randomize
    random.shuffle(loaded_song_paths)

    return render_template("homepage.html", title="Found music", songs=loaded_song_paths)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["GET", "POST"])
def upload_songs():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template("upload_result.html", title="Chyba!", content="Soubor nenalezen!")

        files = request.files.getlist('file')

        filenames = []
        for file in files:
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                return render_template("upload_result.html", title="Chyba!", content="Soubor nebyl vybrán!")
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                if not os.path.exists(UPLOADS_FOLDER):
                    os.mkdir(UPLOADS_FOLDER)

                file.save(os.path.join(UPLOADS_FOLDER, filename))
                filenames.append(filename)

        return render_template("upload_result.html", title="Úspěch!", content=f"Soubory {', '.join(filenames)} byly úspěšně nahrány")
        
    
    elif request.method == 'GET':
        return render_template("upload_page.html")
    
    else:
        return "Chyba!", 400

@app.route('/uploads/<path:filename>', methods=["GET"])
def download_file(filename):

    return send_file(os.path.join(UPLOADS_FOLDER, filename), as_attachment=True)


if __name__ == '__main__':

    if os.path.exists("/certs/fullchain.pem") and os.path.exists("/certs/privkey.pem"):
        app.run(host="0.0.0.0", port=443, ssl_context=('/certs/fullchain.pem', '/certs/privkey.pem'))
    else:
        app.run(host="0.0.0.0", port=443, ssl_context='adhoc')