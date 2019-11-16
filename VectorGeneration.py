import json
from utils import *

# convert spotify_id to a string
#input_json = '{"spotify_id_1": {"name": "Pure Water", "artist": "Migos", "acousticness": 0.7, "volume": 0.2}, "spotify_id_2": {"name": "Cold Water", "artist": "Justin Bieber", "acousticness": 0.9, "volume": 1.6}, "spotify_id_3": {"name": "Hello", "acousticness": 0.7}}'

def vector_generation(sp, isrc_list):
    features_dict = playlist_to_features_dict(isrc_list)
    # print(input_json)
    # print(type(json_data)) : string

    # with open("spotifysongs.json", "r") as f:
    # parsed_json = (json.loads(json_data))
    # print(json.dumps(parsed_json, indent=4, sort_keys=True))

    def common_keys(json_data):
        ar = json_data[next(iter(json_data))]

        ar = {key: 0 for key in ar if type(ar[key]) == float}

        # print("thisisAR:", ar)
        for key in json_data:
            for sub_key in json_data[key]:
                #print("subkey: ", sub_key)
                if type(json_data[key][sub_key]) is float:
                    ar[sub_key] = ar.get(sub_key, 0) + 1

        #for x in range(len(new_json[next(iter(new_json))])):
        for key in ar:
            if ar[key] < len(json_data):
                ar[key] = -1
                # print("this failed, ", key)
        # print("new ar: ", ar)
        return ar


    def generate_arrays(new_json, array):
        final_array = []
        name_of_nums = []
        index = []
        for key in new_json:  # looking at each track's features
            # print("key:", key)
            ar = []
            ar.append(key)
            # print(new_json[key])
            #index.append(new_json[key][0])
            for smallkey in new_json[key]:
                # print("smallkey:", smallkey)
                if array.get(smallkey, 0) != -1:
                    value = new_json[key][smallkey]
                    if type(value) is float:
                        ar.append(value)
                        #if smallkey not in name_of_nums:
                        #    name_of_nums.append(smallkey)
            # print("ar: ", ar)
            final_array.append(ar)
        # print(finalArray)
        return final_array


    def normalize(final):
        for x in range(len(final[0])):  # len(array[0])
            # ar = [max(subArray[x]) for subArray in array if type(subArray[x]) is float]
            ar = []
            for subArray in final:
                # print("subArray: ", subArray[x])
                #print("subarray: ", subArray, " length: ", len(subArray))
                if type(subArray[x]) is float:
                    # print("subArray: ", subArray[x])
                    ar.append(subArray[x])
            # print("ar: ", ar)
            if ar:
                largest_val = max(ar)
                smallest_val = min(ar)
                for subArray in final:
                    if type(subArray[x]) is float:
                        subArray[x] = (subArray[x] - smallest_val) / (largest_val - smallest_val)


    ar = common_keys(features_dict)

    finalArray = generate_arrays(features_dict, ar)

    normalize(finalArray)

    return finalArray

#print(finalArray)

#print("FinalArray: ", finalArray, " namesArray: ", namesArray)