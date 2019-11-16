import os
import sys
import numpy as np
import json
import random
import string

from google.cloud import firestore
import google.cloud.exceptions

db = firestore.Client()

def generate_filter(raw_loaded_genres, name, num):

	#reading genre map
	# with open('genremap_full.json', 'r') as f:
	# 	raw_loaded_genres = json.loads(f.read())

	# #reading moods
	# with open('moods.txt', 'r') as f:
	# 	moods = f.read().split()

	#loading genres, removing punctuation
	#raw_loaded_genres = {"Pop": ["USWB11500157", "QMRSZ1900099", "QMAAK1557429", "USUM71512947", "GMM881600001", "USUM71805991", "QMRSZ1701243", "USSM17200399", "SEBGA1600314", "USWB11401921"], "Dance Pop": ["USWB11500157", "QMRSZ1900099", "QMRSZ1701243", "USWB11401921"], "Indie Pop": ["USWB11500157", "QMRSZ1900099", "QMRSZ1701243", "USWB11401921"], "Alternative": ["USWB11500157", "QMRSZ1900099", "GBKPL1948208", "QMAAK1557429", "USUM71512947", "USUM71213439", "QMRSZ1701243", "GBAAA1200920", "USUM71704118", "TCACP1691026", "USWB11401921"], "Rock": ["QMAAK1557429", "USUM71805991", "USSM17200399", "USUM71704118"], "Indie/Alternative": ["USUM71512947", "USUM71213439", "GBAAA1200920", "GBARL1800037"], "Rap/Hip-Hop": ["USUM71410846", "GMM881600001", "USUM71410846"], "Hip-Hop Hitmakers": ["USUM71410846", "USUM71410846"], "Midwestern Rap/Hip-Hop": ["USUM71410846", "USUM71410846"], "'90s Hip-Hop Hits": ["USUM71410846", "USUM71410846"], "Midwestern Lyricists": ["USUM71410846", "USUM71410846"], "Holiday Music": ["USUM71213439"], "Electronic": ["USUM71213439", "SEBGA1600314"], "Country Pop/Cosmopolitan": ["CAUM71800007"], "Country": ["CAUM71800007"], "AOR": ["USSM17200399"], "Art & Progressive Rock": ["USSM17200399"], "Electropop": ["SEBGA1600314"], "House": ["SEBGA1600314"], "New Age": ["SEBGA1600314"], "Celtic Folk": ["SEBGA1600314"], "Pop Punk": ["USUM71704118"], "Emo": ["USUM71704118"]}

	loaded_genres = {}
	for key in raw_loaded_genres:
		loaded_genres[key.lower().replace('/', ' ').replace('-', ' - ').replace('&', ' & ')] = raw_loaded_genres[key]

	#create genre + mood array
	genre_array = [key for key in loaded_genres]
	new_genre_array = genre_array[:]

	# print("starting keep_genre")

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
					word_embedding = np.array(db.collection('glove').document(word).get().to_dict()['vector_embedding'])
					genre_embedding = [a+b for a,b in zip(genre_embedding, word_embedding)] #Sum the word embeddings
				except:
					continue
			if np.any(genre_embedding):
				genre_embeddings.append(genre_embedding)
			else:
				new_genre_array.remove(genre)
		return genre_embeddings

	#create genre embedding array and index array (dummy array) to feed into knn
	genre_embeddings=np.array(keep_genre(genre_array))
	genre_index = np.array([i for i in range(len(genre_embeddings))])

	# print("finished keep_genre")

	#knn
	from sklearn.neighbors import KNeighborsClassifier
	knn = KNeighborsClassifier(n_neighbors=3)
	knn.fit(genre_embeddings, genre_index)

	# print("finished knn")

	#creates filter based on imput name and number of songs in filter
	def create_filter(title, num_songs):
		title = title.lower().replace('/', ' ').replace('-', ' - ').replace('&', ' & ')
		title_embedding = np.array(keep_genre([title]))
		closest_genres = knn.kneighbors(title_embedding)
		neighbors = closest_genres[1][0]
		genres = [new_genre_array[neighbors[0]], new_genre_array[neighbors[1]], new_genre_array[neighbors[2]]]
		filtered_mix, curr_neighbor = [], 0
		while len(filtered_mix) < num_songs and curr_neighbor <= 2:
			if len(loaded_genres[genres[curr_neighbor]]) >= (num_songs - len(filtered_mix)):
				filtered_mix = list(set().union(filtered_mix, random.sample(loaded_genres[genres[curr_neighbor]], num_songs - len(filtered_mix))))
			else:
				filtered_mix = list(set().union(filtered_mix, loaded_genres[genres[curr_neighbor]]))
			curr_neighbor += 1
		return filtered_mix

	return create_filter(name, num)
