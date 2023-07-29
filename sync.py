import bisect
from typing import List
from providers import Provider
from deezer import Deezer
from spotify import Spotify
from track import Track
from match import Match

# Syncing methods

class Sync:
    '''
    Merges the source playlist into destination playlist. Only pushes unique tracks
        provider_src:  Source provider class, ie Spotify()
        provider_dest: Destination provider class, ie Deezer()
        dest_id:       Playlist id of destination
        src_list:      An array of Track objects to be pushed to destination
    '''
    @staticmethod
    def merge(provider_src:Provider, src_id: int | str, provider_dest: Provider, dest_id: int | str):
        src_list: List[Track] = []
        if type(provider_src) == type(provider_dest):
            src_list = provider_src.get_playlist(src_id)
        else:
            src_list = Sync.cross_match(provider_src=provider_src, src_id=src_id, provider_dest=provider_dest)

        dest_list = provider_dest.get_playlist(dest_id)
        dest_list.sort(key=lambda item: item.id)
        to_push: List[Track] = []

        for track in src_list:
            index = bisect.bisect_left(dest_list, track.id, key=lambda item: item.id)
            if index < len(dest_list) and dest_list[index].id == track.id:
                print(f"[{track.id}] found: {track.title} - {track.artist}")
            else:
                to_push.append(track)
        
        provider_dest.push(dest_id, to_push)

    '''
    Mirrors the two playlists. Will only push unique tracks
        provider_src:  Source provider class, ie Spotify()
        provider_dest: Destination provider class, ie Deezer()
        dest_id:       Playlist id of destination
        track_list:    An array of Track objects to be pushed to destination
    '''
    @staticmethod
    def mirror(provider_src:Provider, src_id: int | str, provider_dest:Provider, dest_id: int | str):
        track_list: List[Track] = []

        if type(provider_src) == type(provider_dest):
            track_list = provider_src.get_playlist(src_id)
        else:
            track_list = Sync.cross_match(provider_src=provider_src, src_id=src_id, provider_dest=provider_dest)

        dest_list: List[Track] = provider_dest.get_playlist(dest_id)
        dest_list.sort(key=lambda item: item.id)

        to_push: List[Track] = []
        for track in track_list:
            index = bisect.bisect_left(dest_list, track.id, key=lambda item: item.id)
            if index < len(dest_list) and track.id == dest_list[index].id:
                print(f'Track exists: [{dest_list[index].id}] {dest_list[index].title} - {dest_list[index].artist}')
            else:
                to_push.append(track)
        
        track_list.sort(key=lambda item: item.id)
        to_remove: List[Track] = []
        for track in dest_list:
            index = bisect.bisect_left(track_list, track.id, key=lambda item: item.id)
            if index < len(track_list) and track_list[index].id == track.id:
                print(f'Track exists: [{track_list[index].id}] {track_list[index].title} - {track_list[index].artist}')
            else:
                to_remove.append(track)


        provider_dest.remove(dest_id, to_remove)
        provider_dest.push(dest_id, to_push)
    
    '''
    Cross matches the tracks from the source provider to the destination provider
        provider_src:  Source provider class, ie Spotify()
        provider_dest: Destination provider class, ie Deezer()
        return:        Array of Tracks that will be pushed to destination
    '''
    @staticmethod
    def cross_match(provider_src:Provider, src_id: int | str, provider_dest:Provider) -> List[Track]:
        track_list = provider_src.get_playlist(src_id)
        output = []
        for index, track in enumerate(track_list):
            print(f'Matching {index + 1}/{len(track_list)}: [{track.id}] {track.title} - {track.artist}')
            result = Match.choose(
                track,
                provider_dest.search(track=track.title, artist=track.artist, album=track.album)
            )

            if not result == None:
                output.append(result)
            else:
                print(f"Track not found: {track.title} - {track.artist}")

        return output
    
# rapCaviar = '37i9dQZF1DX0XUsuxWHRQd'
# getTurnt = '37i9dQZF1DWY4xHQp97fN6'
# bassArcade = '37i9dQZF1DX0hvSv9Rf41p'
# theCore = '37i9dQZF1DWXIcbzpLauPS'
# src = Spotify()
# Sync.merge(src, bassArcade, src, '1XVbWWa6HEGUoTSjItkQCZ')
# Sync.merge(src, theCore, src, '5Z8KPGNOF5zhrJNbXLRQi5')
# Sync.merge(src, getTurnt, src, '1sFtK8Bhp2C6iFtKglLyHh')
# Sync.merge(src, rapCaviar, src, '1sFtK8Bhp2C6iFtKglLyHh')