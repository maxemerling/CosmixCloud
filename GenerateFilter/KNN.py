import os
import sys
import numpy as np
import json
import random
import string
import pygn
import pygn_login

#reading genre map
with open('genremap_full.json', 'r') as f:
	raw_loaded_genres = json.loads(f.read())

#reading moods
with open('moods.txt', 'r') as f:
	moods = f.read().split()

#directory of glove
BASE_DIR_GLOVE = ''
GLOVE_DIR = os.path.join(BASE_DIR_GLOVE, 'glove.6B')

#putting glove into dictionary
embeddings_index = {}
with open(os.path.join(GLOVE_DIR, 'glove.6B.300d.txt'),encoding='utf-8') as f:
	for line in f:
		word, coefs = line.split(maxsplit=1)
		coefs = np.fromstring(coefs, 'f', sep=' ')
		embeddings_index[word] = coefs

#loading genres, removing punctuation
loaded_genres = {}
for key in raw_loaded_genres:
	loaded_genres[key.lower().replace('/', ' ').replace('-', ' ')] = raw_loaded_genres[key]

genre_array = [key for key in loaded_genres] + moods
new_genre_array = genre_array[:]

def keep_genre(genre_array):
	"""A function that takes in an array of different genres and returns an array of genre embeddings. 
	If a word isn't found within Glove, that word is simply taken out of the genre embedding. 
	"""
	genre_embeddings=[]
	for i in range(len(genre_array)): #For each genre
		genre_embedding=np.zeros((300))
		genre = genre_array[i]
		for word in genre.split(): #For each word in each genre
			try: #If the word embedding is found
				word_embedding = embeddings_index[word]
				genre_embedding = [a+b for a,b in zip(genre_embedding, word_embedding)] #Sum the word embeddings
			except:
				continue
		if np.any(genre_embedding):
			genre_embeddings.append(genre_embedding)
		else:
			new_genre_array.remove(genre)
	return genre_embeddings

genre_embeddings=np.array(keep_genre(genre_array))
genre_index = np.array([i for i in range(len(genre_embeddings))])

from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(genre_embeddings, genre_index)

def nearest_word(word):
	word_embedding = np.array(keep_genre([word]))
	closest_words = knn.kneighbors(word_embedding)
	distances, neighbors = closest_words[0][0], closest_words[1][0]
	genres = [new_genre_array[neighbors[0]], new_genre_array[neighbors[1]], new_genre_array[neighbors[2]]]
	print(distances)
	print(genres)

"""
def create_playlist(title, num_ongs):
	timeout = time.time() + 5
	title = title.lower().replace('/', ' ').replace('-', ' ')
	playlist = []
	title_embedding = np.array(keep_genre([[title]]))
	closest_genres = knn_genres.kneighbors(title_embedding)
	#print(closest_genres)
	#for i in range(3):
	#    print(genre_array[closest_genres[1][0][i]][0])
	#print('')
	distances, neighbors = closest_genres[0][0], closest_genres[1][0]
	# adding songs in all three playlists
	#for song in loaded_genres[genre_array[neighbors[0]][0]]:
	#    if len(playlist) < num_songs and song in loaded_genres[genre_array[neighbors[1]][0]] and loaded_genres[genre_array[neighbors[2]][0]]:
	#        playlist.append(song)
	while len(playlist) < num_songs:
		sum_dist = 2*(distances[0] + distances[1] + distances[2])
		genres = [genre_array[neighbors[0]][0], genre_array[neighbors[1]][0], genre_array[neighbors[2]][0]]
		flags = {genres[0]: 1, genres[1]: 1, genres[2]: 1}
		p1, p2, p3 = int((distances[1] + distances[2]) * 100 / sum_dist), int((distances[0] + distances[2]) * 100 / sum_dist), int((distances[0] + distances[1]) * 100 / sum_dist)
		my_list = flags[genres[0]] * [genres[0]] * p1 + flags[genres[1]] * [genres[1]] * p2 + flags[genres[2]] * [genres[2]] * p3
		rand_genre = random.choice(my_list)
		rand_song = 'uninitialized'
		songs_to_input = [i for i in range(len(loaded_genres[rand_genre]))]
		while (rand_song in playlist or rand_song == 'uninitialized') and songs_to_input:
			rand_index = random.choice(songs_to_input)
			songs_to_input.remove(rand_index)
			rand_song = loaded_genres[rand_genre][rand_index]
		if not songs_to_input:
			flags[rand_genre] = 0
		else:
			playlist.append(rand_song)
		if time.time() > timeout:
			break
	return playlist
"""
