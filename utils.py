from spotify import *
from apple import *

song_attributes = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
#estimated from graphs in spotify api documentation
attribute_norm_values = {'acousticness': 0.2, 'danceability': 1, 'energy': 1, 'instrumentalness': 0.05, 'liveness': 0.5, 'loudness': -30, 'speechiness': 0.3, 'valence': 1, 'tempo': 250}
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
        return post_song(isrc, db)[1]

def get_or_post_features(isrc, db):
    doc = db.collection('features').document(isrc)
    snapshot = doc.get()
    if snapshot.exists:
        data_dict = snapshot.to_dict()
        return feature_dict_to_vector(data_dict)
    else:
        return post_song(isrc, db)[0]

def post_song(isrc, db):
    raw_features = get_audio_features(isrc)

    features = {attribute: raw_features[attribute] / attribute_norm_values[attribute] for attribute in song_attributes}

    facts = isrc_to_facts(isrc)
    facts['uri'] = raw_features['uri']

    db.collection('features').document(isrc).set(features)
    db.collection('facts').document(isrc).set(facts)

    return features, facts

def feature_dict_to_vector(feature_dict):
    return [feature_dict[attribute] for attribute in song_attributes]


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