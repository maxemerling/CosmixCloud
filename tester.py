request = {'id': 'party1', 'token': 'BQBDdSvy4hBhlPt5bDj791YZgTDlgoS1CExkMo2P3IcDcV_jqXHRT17XnnjgPEtb6IywOt02KM-OHjiJVixwX5I42uZr6IgnM2A7NQBmqGImipZYMLKSSPLUuXe5C6y_K8DqlZo4n1FASPXi6129U4LWhkj53ftveuvA8OLcbGiiEQ2WcidvcNUKfaGjToJn5cgUajqChgvM',
           'playlist': 'spotify/3ghpr791RE6GXfRDN7hCmS'}

### FOR LOCAL TESTING ONLY
import os
credential_path = "/home/max/Documents/projects/Cosmix/Cloud/serviceAccount.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate('serviceAccount.json')
firebase_admin.initialize_app(cred)
### END FOR LOCAL TESTING ONLY

from main import *

def add1(request):

    # get required arguments
    party_id = request['id']
    combined_id = request['playlist']
    token = request['token']

    #get current list of songs in the party
    #party = db.collection('parties').document('gaymes')
    party = {'allTracks': [], 'averageVector': [0]*9, 'filtTracks': []}
    curr_isrcs = set(party['allTracks']) # all songs that are currently in the playlist
    print("curr isrcs", curr_isrcs)

    # current number of songs in party
    curr_party_size = len(curr_isrcs)
    print("curr party size", curr_party_size)

    # get new songs to add to party
    service, playlist_id = combined_id.split('/')
    playlist_isrcs = set(SERVICES[service]['track_isrcs'](playlist_id, token))
    print('playlist isrcs', playlist_isrcs)

    #find songs that we can actually add (i. e. not already in party)
    unseen_isrcs = list(playlist_isrcs - curr_isrcs)
    print('unseen isrcs!!', unseen_isrcs)

    # only calculate and update stuff if new songs are actually being added
    if unseen_isrcs:

        # get list of song attributes for unseen_isrcs
        new_attributes_tuple_list = []
        unseen_attributes = []
        for isrc in unseen_isrcs:
            #feature_vec = get_or_post_features(isrc, db)
            feature_vec = [0.5, 0.4, 0.3]
            unseen_attributes.append(feature_vec)

            new_attributes_tuple_list.append((isrc, feature_vec))

        # get the current average vector of the party
        curr_avg_vec = [0, 0, 0]
        print('curr_avg_vec', curr_avg_vec)

        # Calculate new average song vector
        new_avg_vec = AverageVector.new_avg_vec(curr_avg_vec, curr_party_size, unseen_attributes)
        print('new_avg_vec', new_avg_vec)

        # fill out the rest of new_attributes_tuple_list with the songs currently in the playlist
        new_attributes_tuple_list.extend([(isrc, get_or_post_features(isrc, db)) for isrc in curr_isrcs])
        print('new_attributes_tuple_list', new_attributes_tuple_list)

        # Calculate new filtTracks list
        new_filt_tracks = AverageVector.new_filt_tracks(new_avg_vec, new_attributes_tuple_list, filt_tracks_size=10)
        print('new filt tracks', new_filt_tracks)

        # update averageVector, allTracks, filtTracks in database
        party_ref = db.collection('parties').document(party_id)
        party_ref.update({'averageVector': list(new_avg_vec)})
        party_ref.update({'filtTracks': new_filt_tracks})
        party_ref.update({'allTracks': firestore.ArrayUnion(unseen_isrcs)})