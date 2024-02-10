from flask import Flask, request, send_file, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import urllib.parse
import random
from tinytag import TinyTag


class CacheUtils:

    # cache variables
    cached_duration_time_formatted = "00:00:00"
    cached_songs_names = list()

    def __init__(self) -> None:
        self.full_cache()


    def full_cache(self) -> None:
        # all cache functions
        self.update_songs_duration_cache()
        self.update_loaded_songs_cache()


    def update_songs_duration_cache(self) -> None:
        loaded_song_names = []
        if os.path.exists(UPLOADS_FOLDER):
            loaded_song_names.extend(os.listdir(UPLOADS_FOLDER))

        else:
            os.mkdir(UPLOADS_FOLDER)
            return


        duration_sec = 0
        
        for song in loaded_song_names:        
            loadedSong = TinyTag.get(os.path.join(UPLOADS_FOLDER, song), duration=True, tags=False)

            try:
                duration_sec += int(loadedSong.duration)
            except Exception as e:
                print(e)

        hours, remainder = divmod(duration_sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_time_formatted = "%02d:%02d:%02d" % (hours, minutes, seconds)

        self.cached_duration_time_formatted = duration_time_formatted

    def update_loaded_songs_cache(self) -> None:

        if os.path.exists(UPLOADS_FOLDER):
            self.cached_songs_names.clear()
            self.cached_songs_names.extend(os.listdir(UPLOADS_FOLDER))
        else:
            os.mkdir(UPLOADS_FOLDER)


    def get_songs_url(self, base_url) -> tuple:
        # join domain with song names
        
        songs_urls = list()

        for song in self.cached_songs_names:
            songs_urls.append(os.path.join(base_url, UPLOADS_FOLDER) + "/" + urllib.parse.quote(song))

        return tuple(songs_urls)


# Config variables
ALLOWED_EXTENSIONS = {"mp3", "mp4", "ogg", "wav", "avi"}
UPLOADS_FOLDER = "uploads"

app = Flask(__name__)
cacheUtils = CacheUtils()



def allowed_file(filename) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def homepage():
    random_songs_urls: tuple = cacheUtils.get_songs_url()
    random.shuffle(random_songs_urls)

    return render_template("homepage.html", title="Found music", duration=cacheUtils.cached_duration_time_formatted, songs=random_songs_urls)


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

            else:
                splitted = file.filename.split(".")
                if(len(splitted) > 1):
                    file_extension = "." + splitted[-1]
                else:
                    file_extension = str()

                return render_template("upload_result.html", title="Chyba!", content=f"Koncovka {file_extension} není podporována!")


        # update cache about songs after upload
        cacheUtils.full_cache()

        return render_template("upload_result.html", title="Úspěch!", content=f"Soubory {', '.join(filenames)} byly úspěšně nahrány")
        
    
    elif request.method == 'GET':
        return render_template("upload_page.html")
    
    else:
        return "Chyba!", 400


@app.route('/uploads/<path:filename>', methods=["GET"])
def download_file(filename):
    return send_file(os.path.join(UPLOADS_FOLDER, filename), as_attachment=True)


if __name__ == '__main__':

    certs_path = os.environ.get('PATH_TO_CERTS_FOLDER')

    if certs_path is None:
        certs_path = "/"

    pub_key_path = os.path.join(certs_path, "fullchain.pem")
    priv_key_path = os.path.join(certs_path, "privkey.pem")

    if os.path.exists(pub_key_path) and os.path.exists(priv_key_path):
        print("[LOG] Using HTTPs cert from environment path")
        app.run(host="0.0.0.0", port=443, ssl_context=(pub_key_path, priv_key_path))
        
    else:
        print("[LOG] Using flask's dummy HTTPs cert")
        app.run(host="0.0.0.0", port=443, ssl_context='adhoc')
