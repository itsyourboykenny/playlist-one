from abc import ABC, abstractclassmethod
from track import Track
from playlist import Playlist
from typing import List
import requests
import json
from datetime import datetime
from requests_oauthlib import OAuth2Session
from urllib.parse import urlencode, quote
from match import Match
from callback import Callback
import random
import hashlib
import base64
import re
import time

'''
This is a pseudo abstract class. All providers added to this program shall inherit from this class.
So long as all methods are implemented it will work with the program.
'''

class Provider(ABC):
    '''
    Calls get/post/delete request
        url:     The endpoint
        method:  The request method (call/get/delete)
        params:  An object of parameters to pass as argument
        headers: An object of request headers
        data:    The payload
        return:  Returns a response object
    '''
    def call(self, url: str = None, method: str = 'get', params: dict = None, headers: dict = None, data: dict = None) -> requests.Response:
        if url == None:
            raise ValueError("You must provide a url")
        
        response = None
        try:
            if method.lower() == 'get':
                response = requests.get(url=url, headers=headers, params=params, data=data)
            elif method.lower() == 'post':
                response = requests.post(url=url, headers=headers, params=params, data=data)
            elif method.lower() == 'delete':
                response = requests.delete(url=url, headers=headers, params=params, data=data)
            else:
                raise ValueError(f'Unknown request method: {method}')
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
                raise error
        
        return response

    '''
    This method takes no parameters, and returns the token as a string
    '''
    def new_token(self) -> str:
        pass

    '''
    This method simply checks if the current token is still valid
    '''
    def token_valid(self) -> bool:
        pass

    '''
    Searches and returns the result in the form of an array of Track objects.
    Requires at least a track name to be specified
        track:    Name of the track
        artist:   Name of the artist
        album:    Name of the album
        explicit: Enable/Disable explicit tracks
        return:   Array of Track objects
    '''
    def search(self, track:str, artist:str = None, album:str = None, explicit:bool = True) -> List[Track]:
        pass

    '''
    Most providers returns the search results in json notation. This method
    Converts the json data to Track objects
        json_data: The json data
        return:    An array of Track objects
    '''
    def json_to_tracks(self, json_data: dict) -> List[Track]:
        pass
    
    '''
    Pushes a list of Track objects to this provider.
        playlist_id: id of the playlist to push to
        track_list:  Array of Track objects to push
    '''
    def push(self, playlist_id, track_list: List[Track]):
        pass

    '''
    Removes tracks in track_list from this provider if it exists
        playlist_id: id of the playlist to remove from
        track_list:  Array of Track objects to remove
    '''
    def remove(self, playlist_id, track_list: List[Track]):
        pass

    '''
    Simply returns the user id
    '''
    def get_user_id(self) -> int|str:
        pass

    '''
    Creates a new playlist to this provider and returns the id of the newly
    created playlist.
        title:       Name of the playlist
        description: Optional if you want to add some text
        album_cover: Must be a url that can be understood by this provider. It's a hit or miss
    '''
    def new_playlist(self, title, description = None, album_cover = None) -> int | str:
        pass
    
    '''
    Simply returns the tracks of a playlist as an array of Track objects
        id: id of the playlist
    '''
    def get_playlist(self, id) -> List[Track]:
        pass
    
    '''
    Converts a single track into a track object
        id: id of the song
    '''
    def get_track(self, id) -> Track:
        pass