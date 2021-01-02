#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
import sys
import spotipy
import spotipy.util as util
import pandas as pd
import numpy as np


# In[4]:


username = 'janelouise14'
scope = 'user-library-read'
redirect_uri = 'http://localhost/'
CLIENT_ID = 'bf24c6fa1c704008954b3d6649d8361c'
CLIENT_SECRET = '653f034695394bc789ecf920eabea75c'
token = util.prompt_for_user_token(username, scope, CLIENT_ID, CLIENT_SECRET, redirect_uri)
sp = spotipy.Spotify(auth=token)


# In[5]:


#Creating Discover Weekly Playlist Dataframe
playlist_id = 'spotify:playlist:37i9dQZEVXcNdUDkhjLdnd'
playlist = sp.user_playlist(username, playlist_id)
tracks = playlist['tracks']['items']
next_uri = playlist['tracks']['next']
for _ in range(int(playlist['tracks']['total'] / playlist['tracks']['limit'])):
    response = sp._get(next_uri)
    tracks += response['items']
    next_uri = response['next']

for track in playlist:
    columns=['id', 'artist', 'name', 'release_date', 'added_at']
    
tracks_df = pd.DataFrame([(track['track']['id'],
                           track['track']['artists'][0]['name'],
                           track['track']['name'])
                          for track in playlist['tracks']['items']],
                         columns=['id', 'artist', 'name'] )


# In[6]:


# Creating Liked Songs Dataframe
# if len(sys.argv) > 1:
#     username = sys.argv[1]
# else:
#     print('Usage: %s janelouise14' % (sys.argv[0],))
#     sys.exit()

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks(limit=50, offset=0)
    for item in results['items']:
        track = item['track']
        tracks = playlist['tracks']['items']
#         print(track['name'] + ' - ' + track['artists'][0]['name'])
        saved_df = pd.DataFrame([(track['track']['id'],
                           track['track']['artists'][0]['name'],
                           track['track']['name'])
                          for track in results['items']],
                         columns=['saveid', 'artist', 'name'] )
else:
    print('This did not work')


# In[7]:


# Dataframe that contains the songs shared between Liked Songs and Discover Weekly
common =     set.intersection(set(saved_df.saveid), set(tracks_df.id))

common_df = pd.DataFrame(common)
shared_df = common_df.rename(columns={0:'saved'})


# In[8]:


# Boolean value column in Discover Weekly Dataframe that determines if song was in Liked Songs or not
tracks_df['liked'] = tracks_df['id'].isin(shared_df['saved'])


# In[9]:


# adding new date column
tracks_df['date'] = pd.to_datetime('today')
tracks_df['date'] = pd.to_datetime(tracks_df['date']).dt.date


# In[10]:


# creating new features columns from Spotify's audio features.
features = []
for n, chunk_series in tracks_df.groupby(np.arange(len(tracks_df)) // 50).id:
    features += sp.audio_features([*map(str, chunk_series)])
features_df = pd.DataFrame.from_dict(filter(None, features))
tracks_with_features_df = tracks_df.merge(features_df, on=['id'], how='inner')


# In[11]:


tracks_with_features_df.to_csv(r'C:\programdata\MySQL\MySQL Server 8.0\Data\employee\DiscoverWeekly.csv', index = False)


# In[12]:


tracks_with_features_df.to_excel(r'C:\Users\janed\OneDrive\Desktop\WeeklyDW.xlsx', index = None)

