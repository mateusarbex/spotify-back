import time
import sys
import redis
import spotipy
import os
import json
import uuid


from flask import Flask, redirect,request,session,abort,Response
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import random

session_token = ''

song_queue = []

load_dotenv()

scope = "user-modify-playback-state user-read-playback-state user-read-private user-read-recently-played"
id = os.environ.get('SPOTIPY_CLIENT_ID')    
secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_ui = os.environ.get('SPOTIPY_REDIRECT_URI')
api_base = os.environ.get('API_BASE')




                                               
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

app = Flask(__name__)
CORS(app,supports_credentials=True)

app.secret_key = 'spoti-back'
cache = redis.Redis(host='redis', port=6379)

@app.before_request
def make_session_permanent():
    session.permanent = True
    try:
        print(session['uuid'])
    except:
        session['uuid'] = uuid.uuid4().hex

@app.route('/')
def get_user():
    try:
        os.remove('.cache')
    except:
        print('ja removido')
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = id, client_secret = secret, redirect_uri = redirect_ui, scope = scope,show_dialog=True)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def get_ip(n):
    return n['ip']

def get_played_tracks():
    sp = spotipy.Spotify(auth=session_token['access_token'])
    songs_played = sp.current_user_recently_played()['items']
    return list(map(lambda x: x['track']['uri'],songs_played))

@app.route('/user')
def get_current_user():
    if not get_token():
        redirect('/')
    sp = spotipy.Spotify(auth=session_token['access_token'])
    return json.dumps(sp.current_user())

@app.route('/get_recent_tracks')
def get_recent_tracks():
    if not get_token():
        redirect('/')
    sp = spotipy.Spotify(auth=session_token['access_token'])
    return json.dumps(sp.current_user_recently_played()['items'][0])

@app.route('/add_to_queue',methods=['POST'])
def add_to_queue():
    global song_queue
    authorized = get_token()
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session_token['access_token']) 
    data = request.get_json() 
    current_track = get_current_track()['uri']
    try:
        index = list(map(lambda x: x['song'],song_queue)).index(current_track)
        song_queue = song_queue[index:]
    except:
        song_queue.append({'song':current_track,'id':uuid.uuid4().hex})
    try:
        if(count_id()<3):
            sp.add_to_queue(data['uri'])
            song_queue.append({'song':data['uri'],'id':session['uuid']})
            return json.dumps({'message':'sucesso','status':200})
        return f'N??mero m??ximo excedido'
    except:
        return abort(Response('Nenhum dispositivo em modo play encontrado'))
        
def count_id():
    try:
        count = list(map(lambda x: x['id'],song_queue)).count(session['uuid'])
        return count
    except:
        print('deu erro')
        return 0

@app.route('/count')
def count_route():
    count = count_id()
    return f'{count} many times'


@app.route('/callback')
def callback():
    global session_token
    session_token = ''
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = id, client_secret = secret, redirect_uri = redirect_ui, scope = scope)
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session_token = token_info
    sp = spotipy.Spotify(auth=session_token['access_token'])
    return redirect("http://spotify-queuer.herokuapp.com/")

@app.route('/playback')
def get_current_track():
    if not get_token():
         return redirect('/')
    sp = spotipy.Spotify(auth=session_token['access_token'])
    current_playback = sp.current_playback()
    if current_playback:
        return current_playback['item']
    return abort(Response('Nenhum dispotivo encontrado'))

# @app.route('/playlist')
# def get_current_playlist():
#     if not get_token():
#         return redirect('/')
#     sp = spotipy.Spotify(auth=session_token['access_token'])
#     sp.current_pla

def get_token():
    global session_token
    token_valid = False
    if not session_token:
        return token_valid
    now = int(time.time())
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = id, client_secret = secret, redirect_uri = redirect, scope = scope)
    session_token = sp_oauth.refresh_access_token(session_token['refresh_token'])
    token_valid = True
    return token_valid


@app.route('/print-session')
def print_session():
   token = session['uuid']
   return f'{token}'

@app.route('/search')
def query():
    query = request.args.get('input')
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    results = spotify.search(query,limit=limit,offset=offset,type="track")

    return results['tracks']


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0",port=port)