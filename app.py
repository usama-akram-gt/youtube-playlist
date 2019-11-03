from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import csv
import pandas
from playlistCreator import youtube_search
from playlistCreator import add_video_to_playlist
from playlistCreator import createPlaylist
import flask
from flask import Flask, render_template, jsonify, request, redirect, url_for
import httplib2
import requests as re
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#from json2html import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

app = Flask(__name__)
CLIENT_SECRETS_FILE = "client2.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
app.secret_key = '!\xa1\xf3P\x13\xc1\xd2y\xafO*\x1a>\xb2\xa6C\xbd\x8a\xe7"\xaf\x95\xbd\xd4'

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
    if 'credentials' not in flask.session:
      return flask.redirect('authorize')
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    playListID = createPlaylist(youtube,df['playlistTitle'][0],df['playlistDescription'][0],df['playlistPrivacy'][0])
    with open('playlist.csv', mode='w') as csv_file:
        fieldnames = ['playlistId']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'playlistId': playListID})
    flask.session['credentials'] = credentials_to_dict(credentials)        
    #print(playListID)
    addVideo()
    return ""

@app.route('/addVideo')
def addVideo():
    print("Add Video!")
    df = pandas.read_csv('videos.csv')
    dw = pandas.read_csv('playlist.csv')
    dp = pandas.read_csv('parameters.csv')
    if 'credentials' not in flask.session:
      return flask.redirect('authorize')
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    add_video_to_playlist(youtube,dp['front_video_id'][0],dw['playlistId'][0])    
    for video in df['videoId']:
        add_video_to_playlist(youtube,video,dw['playlistId'][0])
    flask.session['credentials'] = credentials_to_dict(credentials)
    return ""

@app.route('/searchVideos')
def searchVideos():
    #print('searchVideos')
    df = pandas.read_csv('parameters.csv')
    if 'credentials' not in flask.session:
      return flask.redirect('authorize')
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    youtube_search(youtube,df['searchItem'][0],df['maxResults'][0])
    flask.session['credentials'] = credentials_to_dict(credentials)
    create_Playlist()
    return ""

def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ''

@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.redirect(flask.url_for('test_api_request'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


scheduler = BackgroundScheduler()
scheduler.add_job(func=searchVideos, trigger='cron', hour='10', minute='50')
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)