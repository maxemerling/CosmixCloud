import os
import sys
import numpy as np
import json
import random
import string

# from google.cloud import firestore
# import google.cloud.exceptions

# db = firestore.Client()

#reading genre map
with open('genremap_full.json', 'r') as f:
	raw_loaded_genres = json.loads(f.read())

# #reading moods
with open('moods.txt', 'r') as f:
	moods = f.read().split()

#directory of glove
BASE_DIR_GLOVE = ''
GLOVE_DIR = os.path.join(BASE_DIR_GLOVE, 'glove.6B')

#putting glove into dictionary
embeddings_index = {}
with open(os.path.join(GLOVE_DIR, 'glove.6B.50d.txt'),encoding='utf-8') as f:
	for line in f:
		word, coefs = line.split(maxsplit=1)
		coefs = np.fromstring(coefs, 'f', sep=' ')
		embeddings_index[word] = coefs

#loading genres, removing punctuation
loaded_genres = {}
for key in raw_loaded_genres:
	loaded_genres[key.lower().replace('/', ' ').replace('-', ' ').replace('&', ' & ')] = raw_loaded_genres[key]

#create genre + mood array
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
		word_counter = 0
		for word in genre.split(): #For each word in each genre
			try: #If the word embedding is found
				word_embedding = embeddings_index[word]
				genre_embedding = [a+b for a,b in zip(genre_embedding, word_embedding)] #Sum the word embeddings
				word_counter += 1
			except:
				continue
		# print("org", genre_embedding[0])
		# print(genre_embedding[0])
		if np.any(genre_embedding):
			genre_embeddings.append(genre_embedding)
		else:
			new_genre_array.remove(genre)
	return genre_embeddings

#create genre embedding array and index array (dummy array) to feed into knn
genre_embeddings=np.array(keep_genre(genre_array))
genre_index = np.array([i for i in range(len(genre_embeddings))])

#knn
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(genre_embeddings, genre_index)

#creates filter based on imput name and number of songs in filter
def create_filter(title, num_songs):
	title = title.lower().replace('/', ' ').replace('-', ' ').replace('&', ' & ')
	title_embedding = np.array(keep_genre([title]))
	closest_genres = knn.kneighbors(title_embedding)
	distances, neighbors = closest_genres[0][0], closest_genres[1][0]
	genres = [new_genre_array[neighbors[0]], new_genre_array[neighbors[1]], new_genre_array[neighbors[2]]]
	print(distances)
	print(genres)
	filtered_mix, curr_neighbor = [], 0
	while len(filtered_mix) < num_songs and curr_neighbor <= 2:
		if len(loaded_genres[genres[curr_neighbor]]) >= (num_songs - len(filtered_mix)):
			filtered_mix = list(set().union(filtered_mix, random.sample(loaded_genres[genres[curr_neighbor]], num_songs - len(filtered_mix))))
		else:
			filtered_mix = list(set().union(filtered_mix, loaded_genres[genres[curr_neighbor]]))
		curr_neighbor += 1
	return filtered_mix
