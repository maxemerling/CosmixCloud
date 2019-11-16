import json
from utils import *
from scipy.spatial import distance

song_attributes = {'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo'}
num_attributes = len(song_attributes)
#feature_dict = playlist_to_features_dict(isrc_list)

# def check_attributes(dict):
#     for key in dict:
#         for attribute in song_attributes:
#             if attribute not in dict[key]:
#                 print(key, 'error')

def add_to_mix(new_isrcs, filt_isrcs, avg_vec, total_songs, num):

    all_isrcs = new_isrcs[:].extend(filt_isrcs)
    feature_dict = playlist_to_features_dict(all_isrcs)

    #add to genre database

    #vectorize new_isrcs
    new_isrcs_vec = []
    new_isrcs_avg_vec = [0]*num_attributes
    for isrc in new_isrcs:
        isrc_vec = [isrc] + [0]*num_attributes
        for index, attribute in enumerate(song_attributes):
            isrc_vec[index + 1] = feature_dict[isrc][attribute]
            new_isrcs_avg_vec[index] += isrc_vec[index + 1]
        new_isrcs.append(isrc_vec)

    for i in range(num_attributes):
        new_isrcs_avg_vec[i] /= num_attributes

    #vectorize filt_isrcs
    filt_isrcs_vec = []
    for isrc in filt_isrcs:
        isrc_vec = [isrc] + [0]*num_attributes
        for index, attribute in enumerate(song_attributes):
            isrc_vec[index + 1] = feature_dict[isrc][attribute]
        filt_isrcs_vec.append(isrc_vec)

    all_isrcs_vec = new_isrcs_vec[:].extend(filt_isrcs_vec)

    #new avg of mix
    new_avg_vec = []
    for i in range(num_attributes):
        new_avg_vec[i] = avg_vec[i] * (total_songs - len(new_isrcs)) / total_songs + new_isrcs_avg_vec[i] * len(new_isrcs) / total_songs

    def normalize_vectors(iscrs_vec, new_avg_vec):
        max_vec = []
        for index in range(num_attributes):
            attribute_max = [new_avg_vec[index]]
            for vec in iscrs_vec:
                attribute_max.append(vec[index + 1])
            max_vec.append(max(attribute_max))
        for index in range(num_attributes):
            new_avg_vec[index] /= max_vec[index]
            for vec in iscrs_vec:
                vec[index + 1] /= max_vec[index]

    def similar_songs(iscrs_vec, new_avg_vec, num):
        song_similarity_list = []
        similar_songs = []
        for i in range(len(iscrs_vec)):
            song_similarity_list.append([distance.euclidean(new_avg_vec, iscrs_vec[i][1:]), i])
        song_similarity_list.sort(key = lambda song_pair: song_pair[0])
        for song_pair in song_similarity_list[:num]:
            similar_songs.append(iscrs_vec[song_pair[1]][0])
        return similar_songs

    normalize_vectors(all_isrcs_vec, new_avg_vec)
    new_filt_isrcs = similar_songs(all_isrcs_vec, new_avg_vec, num)

    return new_avg_vec, new_filt_isrcs
