from spotify import *
from apple import *

song_attributes = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
num_attributes = len(song_attributes)

def get_val_from_request(request, key):
    request_json = request.get_json()
    if request.args and key in request.args:
        return request.args.get(key)
    elif request_json and key in request_json:
        return request_json[key]

def get_or_post_facts(isrc, db):
    doc = db.collection('facts').document(isrc)
    snapshot = doc.get()
    if snapshot.exists:
        return snapshot.to_dict()
    else:
        facts = isrc_to_facts(isrc)
        doc.set(facts)
        return facts


def feature_dict_to_vector(feature_dict):
    return [feature_dict[attribute] for attribute in song_attributes]


def get_or_post_features(isrc, db):
    doc = db.collection('features').document(isrc)
    snapshot = doc.get()
    if snapshot.exists:
        data_dict = snapshot.to_dict()
        return feature_dict_to_vector(data_dict)
    else:
        raw_data = get_audio_features(isrc)
        features = {attribute: raw_data[attribute] for attribute in song_attributes}
        doc.set(features)
        return feature_dict_to_vector(features)

def playlist_to_features_dict(isrc_list):
    #user_id = get_val_from_request(request, 'user')
    #playlist_id = get_val_from_request(request, 'playlist')
    d = {}
    for isrc in isrc_list:
        try:
            d[isrc] = get_or_post_features(isrc)
        except:
            continue
    return d