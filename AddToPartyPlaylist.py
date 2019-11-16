from VectorGeneration import *
from SimilarSongs import *

def add_to_party_playlist(sp, isrc_list, num):
	song_list = vector_generation(sp, isrc_list)
	return similar_songs(song_list, num)
