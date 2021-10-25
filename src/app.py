import time
import sys
import redis
import spotipy
import os
import json

from flask import Flask, redirect,request,session
from flask import request
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

session_token = ''

with open('session.json','r') as json_file:
    session_token = json.load(json_file)


load_dotenv()

scope = "user-modify-playback-state"
id = os.environ.get('SPOTIPY_CLIENT_ID')    
secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_ui = os.environ.get('SPOTIPY_REDIRECT_URI')
api_base = os.environ.get('API_BASE')


                                               
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

app = Flask(__name__)
CORS(app)

app.secret_key = 'spoti-back'
cache = redis.Redis(host='redis', port=6379)

@app.route('/')
def get_user():
    if not get_token():
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = id, client_secret = secret, redirect_uri = redirect_ui, scope = scope)
        auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/add_to_queue',methods=['POST'])
def add_to_queue():
    authorized = get_token()
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session_token['access_token'])
    data = request.get_json()
    sp.add_to_queue(data['uri'])
    return 'Track adicionada com sucesso'

@app.route('/callback')
def callback():
    global session_token
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = id, client_secret = secret, redirect_uri = redirect_ui, scope = scope)
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session_token = token_info
    # Saving the access token along with all other token related info
    with open('session.json','w') as outfile:
        json.dump(session_token,outfile)
    return redirect("http://localhost:3000")

def get_token():
    global session_token
    token_valid = False
    if not session_token:
        return token_valid
    now = int(time.time())
    is_token_expired = session_token['expires_at'] - now < 60
    if (is_token_expired):
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = id, client_secret = secret, redirect_uri = redirect, scope = scope)
        session_token = sp_oauth.refresh_access_token(session_token['refresh_token'])
    token_valid = True
    return token_valid

@app.route('/search')
def query():
    query = request.args.get('input')
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    results = spotify.search(query,limit=limit,offset=offset,type="track")

    return results['tracks']

