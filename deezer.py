from providers import *

# See providers.py for documentation

class Deezer(Provider):
    def __init__(self):
        try:
            with open("deezer_token", "r") as file:
                self.token = file.read()
        except FileNotFoundError as error:
            self.token = ""

        self.CODES = {
            4: "QUOTA",
            100: "ITEMS_LIMIT_EXCEEDED",
            200: "PERMISSION",
            300: "TOKEN_INVALID",
            500: "PARAMETER",
            501: "PARAMETER_MISSING",
            600: "QUERY_INVALID",
            700: "SERVICE_BUSY",
            800: "DATA_NOT_FOUND",
            901: "INDIVIDUAL_ACCOUNT_NOT_ALLOWED"
        }

    def new_token(self):
        HOST = 'localhost'
        PORT = 9999
        URL = "https://connect.deezer.com/oauth/auth.php"
        TOKEN = "https://connect.deezer.com/oauth/access_token.php"
        REDIRECT = f"http://{HOST}:{PORT}/callback"

        with open("credentials.json", "r") as file:
            credentials = json.load(file)

        permissions = {
            'app_id': credentials['deezer']['client_id'],
            "perms": "manage_library,delete_library"
        }

        auth = f'{URL}?app_id={permissions["app_id"]}&redirect_uri={REDIRECT}&perms={permissions["perms"]}'
        print(auth)
        server = Callback(host=HOST, port=PORT)
        server.start()
        while server.get_key() == None:
            time.sleep(0.05)
        auth_response = server.get_key()
        server.stop()
        token = self.call(
            url=TOKEN,
            method='get',
            params={
                'app_id': credentials['deezer']['client_id'],
                'secret': credentials['deezer']['client_secret'],
                'code': auth_response,
                'output': 'json'
            }
        ).json()
        self.token = token['access_token']

        with open("deezer_token", "w") as file:
            file.write(self.token)

    def token_valid(self):
        ENDPOINT = "https://api.deezer.com/user/me"
        params = {
            'access_token': self.token,
            'request_type': 'GET'
        }

        result = self.call(url=ENDPOINT, method='get', params=params).json()

        if 'error' in result:
            return False
        else:
            return True

    def search(self, track:str = "", artist:str = "", album:str = "", explicit:bool = True) -> List[Track]:
        if not track:
            raise ValueError("Track cannot be blank")

        ENDPOINT = 'https://api.deezer.com/search'

        attempt = 0
        MAX_ATTEMPT = 3
        while True:
            if attempt > MAX_ATTEMPT:
                return None
            
            output: List[Track] = []
            if attempt < MAX_ATTEMPT:
                track_formatted = f'"{quote(Match.format_search(track, attempt))}"'
                artist_formatted = f'"{quote(Match.format_search(artist, attempt))}"' if artist else ""
                album_formatted = f'"{quote(Match.format_search(album, attempt))}"' if album else ""
                params = {
                    "q": f'track:{track_formatted}{" artist:" + artist_formatted if artist else ""}{" album:" + album_formatted if album else ""}explicit_lyrics: {explicit}'
                }
            else:
                query = f'{Match.format_search(track, 0)} {Match.format_search(artist, 0)}{" " + album if album else ""}'
                params = {
                    "q": f'"{quote(query)}"'
                }

            response = self.call(url=ENDPOINT, params=params, method='get').json()
            output = self.json_to_tracks(response)
            if len(output) >= 1:
                return output
            
            attempt += 1
    
    def json_to_tracks(self, json_data:dict) -> List[Track]:
        output = []

        if 'data' in json_data:
            json_data = json_data['data']
        for track in json_data:
            output.append(Track(
                track["id"],
                track["title"],
                track["artist"]["name"],
                track["album"]["title"],
                track["duration"],
                track["explicit_lyrics"],
                0,
                0 if track['album']['type'] == 'album' else 1 if track['album']['type'] == 'single' else 2
            ))
        return output
    
    def push(self, playlist_id, track_list: List[Track]):
        if not self.token_valid():
            self.new_token()

        to_push = len(track_list)
        if to_push < 1:
            return
        curr_index = 0
        
        while curr_index < to_push:
            songs = ''
            read_count = 0
            while read_count < 100 and curr_index < to_push:
                songs += f'{track_list[curr_index].id},'
                curr_index += 1
                read_count += 1
            ENDPOINT = f'https://api.deezer.com/playlist/{playlist_id}/tracks'
            header = {
                'Content-Type': 'application/json'
            }
            params = {
                'access_token': self.token,
                'request_method': 'POST',
                'songs': songs
            }

            response = self.call(method='post', url=ENDPOINT, headers=header, params=params).json()
            if response != True and 'error' in response:
                raise ValueError(response['error']['message'])
    
    def remove(self, playlist_id, track_list: List[Track]):
        if not self.token_valid():
            self.new_token()

        ENDPOINT = f"https://api.deezer.com/playlist/{playlist_id}/tracks"

        track_index = 0
        while track_index < len(track_list):
            songs = ''
            count = 0
            while count < 100 and track_index < len(track_list):
                songs += f'{track_list[track_index].id},'
                track_index += 1
                count += 1
            params = {
                'access_token': self.token,
                'songs': songs
            }
            
            response = self.call(url=ENDPOINT, method='delete', params=params).json()
            if response != True and 'error' in response:
                raise ValueError(response['error']['message'])


    def get_user_id(self) -> int|str:
        if not self.token_valid():
            self.new_token()
        ENDPOINT = "https://api.deezer.com/user/me"
        params = {
            'access_token': self.token,
            'request_type': 'GET'
        }

        try:
            response = requests.get(url=ENDPOINT, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f'Request Error: {error}')
        
        result = response.json()
        return result['id']


    def new_playlist(self, title, description = "", album_cover = "") -> int | str:
        if not self.token_valid():
            self.new_token()
        ENDPOINT = f"https://api.deezer.com/user/{self.get_user_id()}/playlists"
        params = {
            'access_token': self.token,
            "title": title,
            'description': description,
            'picture': album_cover
        }

        response = requests.post(url=ENDPOINT, params=params)
        playlist_id = response.json()['id']

        playlist_url = f'https://api.deezer.com/playlist/{playlist_id}'
        response = requests.post(url=playlist_url, params=params)
        result = response.json()
        print(result)
        
        return playlist_id
    
    def get_playlist(self, id) -> List[Track]:
        if not self.token_valid():
            self.new_token()
        
        ENDPOINT = f'https://api.deezer.com/playlist/{id}/tracks'
        limit = 100
        
        output = []
        result = self.call(
            url=ENDPOINT,
            method='get',
            params={
                'access_token': self.token,
                'limit': limit
            }
        ).json()
        if 'error' in result:
            raise ValueError(f"[ID:{id}] {result['error']['code']} {self.CODES[result['error']['code']]}: " + result['error']['message'])
        output = self.json_to_tracks(result)
        got = len(result['data'])
        total = result['total']
        offset = 1

        while got < total:
            result = self.call(
                url=ENDPOINT,
                method='get',
                params={
                    'access_token': self.token,
                    'index': offset * limit,
                    'limit': limit
                }
            ).json()
            output += self.json_to_tracks(result)
            got += len(result['data'])
            offset += 1
        
        return output
    
    def get_track(self, id) -> Track:
        ENDPOINT = f"https://api.deezer.com/track/{id}"
        try:
            response = requests.get(ENDPOINT)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f"Request Error: {error}")
        
        result = response.json()
        return self.json_to_tracks([result])[0]