from providers import *
from deezer import Deezer
from spotify import Spotify
from typing import List
from sync import Sync
import argparse
import sys

'''
This program will not work without the credentials.json file. This file should contain
your client_id and client_secret from your developer account. This program is fully
sandboxed, therefore you are expected to have your own account.

Currently only Spotify and Deezer is fully supported. Apple Music will be added once
it makes sense for me to pay for a developer account.

Example credentials.json
{
    "spotify": {
        "client_id": "jguiwenkluu8sanj32we89vsnfsa903",
        "client_secret": "ja8gjkl348sgn3489sgvnl23qv92qn"
    },

    "deezer": {
        "client_id": "jguiwenkluu8sanj32we89vsnfsa903",
        "client_secret": "ja8gjkl348sgn3489sgvnl23qv92qn"
    },

    "amazon": {
        "client_id": "jguiwenkluu8sanj32we89vsnfsa903",
        "client_secret": "ja8gjkl348sgn3489sgvnl23qv92qn"
    },

    "lastfm": {
        "client_id": "jguiwenkluu8sanj32we89vsnfsa903",
        "client_secret": "ja8gjkl348sgn3489sgvnl23qv92qn"
    }
}
'''

# def printHelp():
#     print(
#         "usage: python3 pl1.py --src provider --dest provider --toid id --fromid id --method method\n"
#         "Supported providers: spotify, deezer\n"
#         "id: Playlist id of the providers\n"
#         "Methods: mirror/merge"
#     )

parser = argparse.ArgumentParser()
parser.add_argument('--src', type=str, help="Source provider (spotify/deezer)")
parser.add_argument('--dest', type=str, help="Destination provider (spotify/deezer)")
parser.add_argument('--method', type=str, help="Syncing method. Either 'mirror' or 'merge'")
parser.add_argument('--fromid', type=str, help='Playlist id of source provider')
parser.add_argument('--toid', type=str, help='Playlist id of destination provider')
parser = parser.parse_args()

if (parser.help):
    # printHelp()
    sys.exit(1)

# Preliminary checks. All values must be present
src:str = parser.src
if (not src or len(src) < 1):
    print("You must provide a source provider")
    # printHelp()
    sys.exit(1)

dest:str = parser.dest
if (not dest or len(dest) < 1):
    print("You must provide a destination provider")
    # printHelp()
    sys.exit(1)

method:str = parser.method
if (not method or len(method) < 1):
    print('You must provide a syncing method')
    # printHelp()
    sys.exit(1)

fromid:str = parser.fromid
if (not fromid or len(fromid) < 1):
    print("You must provide the source playlist id")
    # printHelp()
    sys.exit(1)

toid:str = parser.toid
if (not toid or len(toid) < 1):
    print("You must provide a destination playlist id")
    # printHelp()
    sys.exit(1)

# Load the requested provider class
providers:List[Provider] = [Provider, Provider]
for index, x in enumerate([src, dest]):
    match x:
        case 'spotify':
            providers[index] = Spotify()
        case 'deezer':
            providers[index] = Deezer()
        case _:
            print("Invalid provider")
            sys.exit(1)

# Run the requested method
match method:
    case 'mirror':
        Sync.mirror(provider_src=providers[0], src_id=fromid, provider_dest=providers[1], dest_id=toid)
    case 'merge':
        Sync.merge(provider_src=providers[0], src_id=fromid, provider_dest=providers[1], dest_id=toid)
    case _:
        print('Invalid sync method')
        sys.exit(1)