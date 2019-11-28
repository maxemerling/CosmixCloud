from google.cloud import firestore
import google.cloud.exceptions
import utils
#from utils import get_val_from_request
# import json
# import secrets
import string
import AverageVector

from VectorGenerationNew import num_attributes, add_to_mix
from schema import Playlist
from GenerateFilter.GenerateFilterDB import *
from napster import *
from AddToPartyPlaylist import *
#from VectorGenerationNew import *

CODE_ALPHABET = string.ascii_letters + string.digits

db = firestore.Client()

SERVICES = {
    'apple': {
        'playlists': utils.apple_playlists,
        'track_isrcs': utils.apple_track_isrcs,
    },
    'spotify': {
        'playlists': utils.spotify_playlists,
        'track_isrcs': utils.spotify_track_isrcs,
    }
}

def new_party(request):
    party_id = get_val_from_request(request, 'id')
    db.collection('parties').document(party_id).set({'allTracks': [], 'filtTracks': [], 'averageVector': [0]*num_attributes})
    return 'Success'


def check_party(request):
    party_id = get_val_from_request(request, 'id')
    return json.dumps(dict(result=db.collection('parties').document(party_id).get().exists))

    #party_id = get_val_from_request(request, 'id')
    #party_ref = db.collection('parties').document(party_id)


    #try:
    #    party_ref.get().to_dict()
    #    return 'Found'
    #except google.cloud.exceptions.NotFound:
    #    return 'Not found'


# def get_facts(request):
#     isrcs = get_val_from_request(request, 'isrc').split('-')
#     try:
#         return json.dumps([get_or_post_facts(isrc, db) for isrc in isrcs])
#     except:
#         print("FAILED WITH", isrcs)
#         print(type(isrcs))

def get_facts_list(request):
    party_id = get_val_from_request(request, 'id')
    isrc_dict = db.collection('parties').document(party_id).get().get('filtTracks')
    return json.dumps([get_or_post_facts(isrc, db) for isrc in isrc_dict])

def gen_filter(request):
    filter_name = get_val_from_request(request, 'name')
    num_songs = get_val_from_request(request, 'numSongs')
    party_id = get_val_from_request(request, 'id')

    all_isrcs = db.collection('parties').document(party_id).get().to_dict()['allTracks']

    genre_dict = create_genre_json(all_isrcs)

    print('finished creating genre dict')
    new_isrcs = generate_filter(genre_dict, filter_name, int(num_songs), db=db)

    return json.dumps([get_or_post_facts(isrc, db) for isrc in new_isrcs])

def save_isrcs(request):
    isrc_list = get_val_from_request(request, "isrcs")
    playlist_name = get_val_from_request(request, "name")
    token = get_val_from_request(request, "token")
    utils.new_playlist(playlist_name, isrc_list, token)

def playlists(request):
    """Return the user's playlists for a given token and service."""
    service = get_val_from_request(request, 'service')
    token = get_val_from_request(request, 'token')
    playlists = list(SERVICES[service]['playlists'](token))
    dict_playlists = [dict(id=service + '/' + p.id, name=p.name, image=p.image) for p in playlists]
    return json.dumps(dict_playlists)


def add(request):

    # get required arguments
    party_id = get_val_from_request(request, 'id')
    combined_id = get_val_from_request(request, 'playlist')
    token = get_val_from_request(request, 'token')

    #get current list of songs in the party
    party = db.collection('parties').document(party_id).get().to_dict()
    curr_isrcs = set(party['allTracks']) # all songs that are currently in the playlist

    # current number of songs in party
    curr_party_size = len(curr_isrcs)

    # get new songs to add to party
    service, playlist_id = combined_id.split('/')
    playlist_isrcs = set(SERVICES[service]['track_isrcs'](playlist_id, token))

    #find songs that we can actually add (i. e. not already in party)
    unseen_isrcs = list(playlist_isrcs - curr_isrcs)

    # only calculate and update stuff if new songs are actually being added
    if unseen_isrcs:

        #storing song genres in database
        # for isrc in unseen_isrcs:
        #     genres = [genre(g)['name'] for g in track(isrc)['links']['genres']['ids']]
        #     for g in genres:
        #         g = g.lower().replace('/', ' ').replace('-', ' - ').replace('&', ' & ')
        #         print(g)
        #         if db.collection('genres').document(g).get().exists:
        #             db.collection('genres').document(g).update({'tracks': firestore.ArrayUnion([isrc])})
        #         else:
        #             db.collection('genres').document(g).set({'tracks': [isrc]})

        # get list of song attributes for unseen_isrcs
        new_attributes_tuple_list = []
        unseen_attributes = []
        for isrc in unseen_isrcs:
            feature_vec = get_or_post_features(isrc, db)
            unseen_attributes.append(feature_vec)

            new_attributes_tuple_list.append((isrc, feature_vec))

        # get the current average vector of the party
        curr_avg_vec = party['averageVector']

        # Calculate new average song vector
        new_avg_vec = AverageVector.new_avg_vec(curr_avg_vec, curr_party_size, unseen_attributes)

        # fill out the rest of new_attributes_tuple_list with the songs currently in the playlist
        new_attributes_tuple_list.extend([(isrc, get_or_post_features(isrc, db)) for isrc in curr_isrcs])

        # Calculate new filtTracks list
        new_filt_tracks = AverageVector.new_filt_tracks(new_avg_vec, new_attributes_tuple_list, filt_tracks_size=10)

        # update averageVector, allTracks, filtTracks in database
        party_ref = db.collection('parties').document(party_id)
        party_ref.update({'averageVector': list(new_avg_vec)})
        party_ref.update({'filtTracks': new_filt_tracks})
        party_ref.update({'allTracks': firestore.ArrayUnion(unseen_isrcs)})


# JAMES'S ADD
#
# def add(request):
#     party_id = get_val_from_request(request, 'id')
#     combined_id = get_val_from_request(request, 'playlist')
#     token = get_val_from_request(request, 'token')
#
#     party_ref = db.collection('parties').document(party_id)
#
#     service, playlist_id = combined_id.split('/')
#     playlist_isrcs = set(SERVICES[service]['track_isrcs'](playlist_id, token))
#
#     party = db.collection('parties').document(party_id).get().to_dict()
#     old_party_isrcs = set(party['allTracks'])
#     # filt_isrcs = party['filtTracks']
#     avg_vec = party['averageVector']
#
#     new_isrcs = playlist_isrcs - old_party_isrcs
#
#     new_avg_vec = AverageVector.new_avg_vec(avg_vec, len(old_party_isrcs), [get_or_post_features(isrc=isrc, db=db) for isrc in new_isrcs])
#
#     if new_isrcs:
#         party_ref.update({'allTracks': firestore.ArrayUnion(new_isrcs)})
#
#     new_filt_isrcs = AverageVector.new_filt_tracks(new_avg_vec, [{isrc: get_or_post_features(isrc=isrc, db=db)} for isrc in (old_party_isrcs & playlist_isrcs)])
#
#     # new_isrcs = list(set(playlist_isrcs) - set(mix_isrcs).union(set(playlist_isrcs)))
#     #
#     # new_avg_vec, new_filt_isrcs = add_to_mix(new_isrcs, filt_isrcs, avg_vec, len(mix_isrcs), num=10)
#     #
#
#     if new_isrcs:
#         party_ref.update({'averageVector': new_avg_vec})
#         party_ref.update({'filtTracks': new_filt_isrcs})

#ORIGINAL ADD

# def add(request):
#     """Add all songs from a given playlist to the group's music."""
#     party_id = get_val_from_request(request, 'id')
#     combined_id = get_val_from_request(request, 'playlist')
#     token = get_val_from_request(request, 'token')
#
#     party_ref = db.collection('parties').document(party_id)
#
#     service, playlist_id = combined_id.split('/')
#     track_isrcs = SERVICES[service]['track_isrcs'](playlist_id, token)
#
#     party_ref.update({'allTracks': firestore.ArrayUnion(track_isrcs)})
#     party = db.collection('parties').document(party_id).get().to_dict()
#     isrcs = party['allTracks']
#
#     sp = spotipy.Spotify(auth=token)
#     party_ref.update({'filtTracks': add_to_party_playlist(sp, isrcs, num=10)})

def save(request):
    """Add filtered songs to a playlist."""
    party_id = get_val_from_request(request, 'id')
    name = get_val_from_request(request, 'name')
    token = get_val_from_request(request, 'token')

    party = db.collection('parties').document(party_id).get().to_dict()
    isrcs = party['filtTracks']
    utils.new_playlist(name, isrcs, token)
