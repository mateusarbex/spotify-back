import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"
print('teste')

SPOTIPY_CLIENT_ID='19d93bb1f98a4356aec5eb71f01568ca'
SPOTIPY_CLIENT_SECRET='4ecc74b6afd74cc2892229a54583742e'
SPOTIPY_REDIRECT_URI='http://localhost:3000'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))
results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])