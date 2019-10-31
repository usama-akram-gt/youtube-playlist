from playlistCreator import get_authenticated_service
from playlistCreator import youtube_search
from playlistCreator import add_video_to_playlist
from playlistCreator import createPlaylist
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/youtube_playlist"
db = SQLAlchemy(app)

class Parametrs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    searchItem = db.Column(db.String(50), unique=False, nullable=False)
    maxResults = db.Column(db.Integer, unique=False, nullable=False)
    playlistTitle = db.Column(db.String(150), unique=False, nullable=False)
    playlistDescription = db.Column(db.String(300), unique=False, nullable=False)
    privacy = db.Column(db.String(30), unique=False, nullable=False)

@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/setParameters', methods={'GET','POST'})
def setParametrs():
    if(request.method == 'POST'):
        searchItem = request.form.get('searchItem')
        maxResults = request.form.get('maxResults')
        playlistTitle = request.form.get('playlistTitle')
        playlistDescription = request.form.get('playlistDescription')
        privacy = request.form.get('privacy')
        entry = Parametrs(searchItem = searchItem, maxResults = maxResults, playlistTitle=playlistTitle,playlistDescription=playlistDescription, privacy = privacy)
        db.session.add(entry)
        db.session.commit()
    print("Set Parametrs!")
    return ""


@app.route('/createPlaylist')
def create_Playlist():
    print("Create Playlist!")
    youtube = get_authenticated_service()
    playListID = createPlaylist(youtube,'Hello Playlist','Newer Description Test','private')
    print(playListID)
    return ""

@app.route('/addVideo')
def addVideo():
    print("Add Video!")
    youtube = get_authenticated_service()
    add_video_to_playlist(youtube,'dUj2XBiQ9Gc','PL_USY7oz1yS9u1dALUZmcaYCgMG4ez1fM')
    return ""

@app.route('/searchVideos')
def searchVideos():
    print('searchVideos')
    youtube = get_authenticated_service()
    youtube_search(youtube,'iPad',10)
    return ""


if __name__ == '__main__':
    app.run(debug=True)