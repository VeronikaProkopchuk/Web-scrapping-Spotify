import requests
import json
import operator

from collections import Counter

from auth import Auth

def main():

    base_url = 'https://api.spotify.com/v1/'
    image_file_name = "album_cover.jpg"
    json_file_name = "spotify_data.json"
    list_of_song_params_to_get = ["tempo","acousticness","danceability","energy","instrumentalness","liveness","loudness","valence"]

    #authorization
    auth = Auth()
    auth.generate_token()    # use it only for the first time
    token = auth.get_token()

    #headers
    headers = {
        'Authorization': f'Bearer {token}',
        "Accept": "application/json"
    }

    #all params except songs info
    params_for_top = {
        'limit' : 10 
    }
    params_for_album_followers = {
        'fields' : "followers.total"
    }

    #all endpoints except songs info
    end_point_top = "me/top/"
    end_end_point_artists = "artists"
    end_end_point_tracks = "tracks"

    end_point_playlist = "playlists/37i9dQZF1DWWGFQLoP9qlv/"
    end_end_point_playlist_cover = "images"

    end_point_song_info = "audio-features"

    #all responses except songs info
    response_top_artists = requests.get(base_url+end_point_top+end_end_point_artists, headers=headers, params=params_for_top)

    response_top_tracks = requests.get(base_url+end_point_top+end_end_point_tracks, headers=headers, params=params_for_top)

    response_for_playlist_cover = requests.get(base_url+end_point_playlist+end_end_point_playlist_cover, headers=headers)

    response_for_playlist_cover_image = requests.get(response_for_playlist_cover.json()[0]['url'])

    response_for_playlist_folovers = requests.get(base_url+end_point_playlist, headers=headers, params=params_for_album_followers)

    response_for_playlist_songs = requests.get(base_url+end_point_playlist+end_end_point_tracks, headers=headers)


    #creating user favorite genres rating

    user_favorite_geners = get_users_favorite_geners(response_top_artists.json())

    #extracting song ids from album information
    song_ids = ""

    total_songs = response_for_playlist_songs.json()['total']

    for item in range(total_songs):
        song_ids = song_ids + (f"{response_for_playlist_songs.json()['items'][item]['track']['id']}")
        if item != total_songs-1:
            song_ids = song_ids + ","

    #params for songs info
    params_for_songs_info = {
        'ids': f"{song_ids}"
    }

    #responce for songs info
    response_for_songs_info = requests.get(base_url+end_point_song_info, headers=headers, params=params_for_songs_info)

    #getting mean values of given params
    mean_values = {}
    for param in range(len(list_of_song_params_to_get)):
        mean_values[list_of_song_params_to_get[param]] = get_mean_value(list_of_song_params_to_get[param], total_songs, response_for_songs_info.json())

    #writing information into files
    with open(image_file_name, 'wb') as file:
        file.write(response_for_playlist_cover_image.content)


    with open(json_file_name, 'w') as file:
            json.dump({'Top 10 artists': response_top_artists.json(), 
                    'Top 5 Genres': user_favorite_geners, 
                    'Top 10 listened Songs': response_top_tracks.json(), 
                    'Playlist Total Followers' : response_for_playlist_folovers.json(), 
                    'Album Tracks Mean Information': mean_values}, file, indent = 4)

#finds out users favorite geners and returns dict where key is gener and value is rating of gener(how much times it repeated)
def get_users_favorite_geners(response_top_artists):
    user_geners = []
    user_favorite_geners = {}
    for artist in range(len(response_top_artists["items"])):
        user_geners += response_top_artists["items"][artist]["genres"]
    user_favorite_geners = Counter(user_geners)
    user_favorite_geners = dict(list(sorted(user_favorite_geners.items(), key=operator.itemgetter(1),reverse=True))[:5])
    return user_favorite_geners

#function to get mean values of song params
def get_mean_value(parametr, total_songs, response):
    value = 0
    for song in range(total_songs):
        value += response["audio_features"][song][parametr]
    value /= total_songs
    return value

if __name__ == "__main__":
    main()