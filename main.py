import os
import spotipy
import requests
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

# Constants
URL = "https://www.billboard.com/charts/hot-100/"
CLIENT_ID = os.environ["MY_CLIENT_ID"]
CLIENT_SECRET = os.environ["MY_CLIENT_SECRET"]

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD (e.g. 2023-07-27): ")

# Scraping Billboard 100
response = requests.get(URL + date)
webpage = response.text

soup = BeautifulSoup(webpage, "html.parser")
title = soup.title.string.split("–")[0]
formatted_title = title + "(" + date + ")"

# Finding top 100 songs from the user input date
songs = soup.find_all(name="h3", class_="a-no-trucate")

# Creating list of top 100 songs
song_list = [song.getText().strip() for song in songs]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# Searching Spotify for songs by title
song_uris = []
year = date.split("-")[0]
for song in song_list:
    try:
        result = sp.search(q=f"track:{song} year:{year}", type="track")
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

print(f"\nNumber of songs found: {len(song_uris)}")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
print(f"New playlist '{date} Billboard 100' successfully created on Spotify!")


# ..........................Uncomment to write to a file Top 100 Songs List..........................
# serial = 1
# with open("top-100-songs.txt", mode="w") as file:
#     file.write(f"{formatted_title}\n")
#     for song in song_list:
#         file.write(f"{serial}. {song}\n")
#         serial += 1
#
# print("Done")
