import numpy as np
from scipy.spatial import distance


def new_avg_vec(old_avg_vec, old_party_size, new_attributes):
    """
    :param old_avg_vec: the previous average vector
    :param old_party_size: the number of songs in the party (for weighting with the vector)
    :param new_attributes: song attributes for new songs that were not already in the party
    """

    avg = np.array(old_avg_vec) * old_party_size
    for attribute_vec in new_attributes:
        avg = avg + attribute_vec

    return avg / float(old_party_size + len(new_attributes))


def new_filt_tracks(new_avg_vec, new_all_tracks, filt_tracks_size):
    """
    :param new_avg_vec: the new average vector of the playlist
    :param new_all_tracks: a list of tuples where the first element is the isrc and the second element is the vector of song attributes
    :param filt_tracks_size: the number of best songs that should be found
    """

    isrcs = []

    i = 0
    while new_all_tracks and i < filt_tracks_size:
        best_pair = min(new_all_tracks, key=lambda pair: distance.euclidean(new_avg_vec, pair[1]))
        new_all_tracks.remove(best_pair)
        isrcs.append(best_pair[0])
        i += 1

    return isrcs
