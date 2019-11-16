from spotify import *
from apple import *

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

def get_or_post_features(isrc, db):
    doc = db.collection('features').document(isrc)
    snapshot = doc.get()
    if snapshot.exists:
        return snapshot.to_dict()
    else:
        features = get_audio_features(isrc)
        doc.set(features)
        return features

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