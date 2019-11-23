import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import secretstuff
from schema import Playlist

client_credentials_manager = SpotifyClientCredentials(secretstuff.spotify_client_id, secretstuff.spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def next_or_null(it, key):
    if len(it) > 0:
        return it[0][key]
    return None

def spotify_playlists(token):
    sp = spotipy.Spotify(auth=token)
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        yield Playlist(id=playlist['id'],
                       name=playlist['name'],
                       image=next_or_null(playlist['images'], key='url')
        )

def id_to_isrc(spotify_id):
    """Convert a spotify id to an isrc."""
    return sp.track(spotify_id)['external_ids']['isrc']

def isrc_to_id(isrc):
    return sp.search(q='isrc:{}'.format(isrc), type='track')['tracks']['items'][0]['id']

def features_from_id(spotify_id):
    return sp.audio_features(spotify_id)[0]

def isrc_to_facts(isrc):
    track = sp.track(isrc_to_id(isrc))
    return {'name': track['name'], 'artist': track['artists'][0]['name'], 'image': track['album']['images'][1]['url']}

def get_audio_features(isrc):
    #isrc = get_val_from_request(request, 'isrc')
    return features_from_id(isrc_to_id(isrc))

def spotify_track_isrcs(playlist_id, token):
    sp = spotipy.Spotify(auth=token)
    isrc_list = []
    for item in get_playlist_tracks(playlist_id)['items']:
        spotify_id = item['track']['id']
        isrc_list.append(id_to_isrc(spotify_id))
    return isrc_list

def get_playlist_tracks(playlist_id, limit=100, offset=0):
    """
    Get full details of the tracks of a playlist owned by a Spotify user. Link to api doc as of 08/17/2019:
        - https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlists-tracks/
    Parameters:
        - playlist_id: the id of the playlist
        - limit: maximum number of tracks to return
        - offset: index of the first track to return
    """
    plid = sp._get_id('playlist', playlist_id)
    return sp._get("playlists/{}/tracks?limit={}&offset={}".format(plid, limit, offset))

def new_playlist(name, isrcs, token):
    sp = spotipy.Spotify(auth=token)
    uid = sp.me()['id']

    playlists = sp.user_playlists(uid)['items']
    matching = [p for p in playlists if p['name'] == name]
    if matching:
        playlist = matching[0]
    else:
        playlist = sp.user_playlist_create(uid, name, public=False)
    ids = [isrc_to_id(isrc) for isrc in isrcs]

    sp.user_playlist_add_tracks(uid, playlist['id'], ids)

def playlist_add_tracks(playlist_id, tracks, position=None):
    plid = sp._get_id('playlist', playlist_id)
    ftracks = [sp._get_uri('track', tid) for tid in tracks]
    return sp._post("playlists/%s/tracks" % plid,
                      payload=ftracks, position=position)