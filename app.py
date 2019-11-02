from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import csv
import pandas
from playlistCreator import get_authenticated_service
from playlistCreator import youtube_search
from playlistCreator import add_video_to_playlist
from playlistCreator import createPlaylist
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def hello():
    Message = 'hide'
    return render_template("index.html", message = Message)

@app.route('/setParameters', methods={'GET','POST'})
def setParametrs():
    if(request.method == 'POST'):
        searchItem = request.form.get('searchItem')
        maxResults = request.form.get('maxResults')
        playlistTitle = request.form.get('playlistTitle')
        playlistDescription = request.form.get('playlistDescription')
        privacy = request.form.get('privacy')
        front_video_id = request.form.get('front_video_id')        
        with open('parameters.csv', mode='w') as csv_file:
            fieldnames = ['searchItem', 'maxResults', 'playlistTitle', 'playlistDescription', 'playlistPrivacy', 'front_video_id']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'searchItem': searchItem, 'maxResults': maxResults, 'playlistTitle': playlistTitle, 'playlistDescription': playlistDescription, 'playlistPrivacy': privacy, 'front_video_id': front_video_id})        
    print("Set Parametrs!")
    Message = 'show'
    return render_template("index.html", message = Message)


@app.route('/createPlaylist')
def create_Playlist():
    print("Create Playlist!")
    df = pandas.read_csv('parameters.csv')
    youtube = get_authenticated_service()
    playListID = createPlaylist(youtube,df['playlistTitle'][0],df['playlistDescription'][0],df['playlistPrivacy'][0])
    with open('playlist.csv', mode='w') as csv_file:
        fieldnames = ['playlistId']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'playlistId': playListID})        
    #print(playListID)
    addVideo()
    return ""

@app.route('/addVideo')
def addVideo():
    print("Add Video!")
    df = pandas.read_csv('videos.csv')
    dw = pandas.read_csv('playlist.csv')
    dp = pandas.read_csv('parameters.csv')
    youtube = get_authenticated_service()
    add_video_to_playlist(youtube,dp['front_video_id'][0],dw['playlistId'][0])    
    for video in df['videoId']:
        add_video_to_playlist(youtube,video,dw['playlistId'][0])
    return ""

@app.route('/searchVideos')
def searchVideos():
    #print('searchVideos')
    df = pandas.read_csv('parameters.csv')
    youtube = get_authenticated_service()
    youtube_search(youtube,df['searchItem'][0],df['maxResults'][0])
    create_Playlist()
    return ""


def automation():
    searchVideos()
    create_Playlist()
    addVideo()
    return ""


scheduler = BackgroundScheduler()
scheduler.add_job(func=searchVideos, trigger='cron', hour='10', minute='50')
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)