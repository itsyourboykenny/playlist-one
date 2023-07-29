from providers import *

# See providers.py for documentation

class Spotify(Provider):
    def __init__(self) -> None:
        self.token = ""
        self.id = 0
        self.CODES = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }

        try:
            with open("spotify_token", "r") as file:
                self.token = file.read()
                if not self.token_valid():
                    self.new_token()
                self.id = self.get_user_id()
        except FileNotFoundError as error:
            self.token = ""

    def new_token(self):
        HOST = 'localhost'
        PORT = 8888
        URL = "https://accounts.spotify.com/authorize"
        TOKEN = "https://accounts.spotify.com/api/token"
        CALLBACK = f"http://{HOST}:{PORT}/callback"

        def generate_string(length: int):
            CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            output: str = ''
            for x in range(0, length):
                output += CHARS[random.randint(0, len(CHARS) - 1)]
            return output
        
        def format_base64(string: str):
            output: str = re.sub(r'\+', '-', string)
            output = re.sub(r'\/', '_', output)
            output = re.sub(r'=+$', '', output)
            return output
        
        verifier = generate_string(128)
        hash_obj = hashlib.sha256(verifier.encode())
        hash_digest = hash_obj.digest()
        challenge_code = base64.b64encode(hash_digest)
        challenge_code = format_base64(challenge_code.decode())

        state = generate_string(16)
        
        with open("credentials.json", "r") as file:
            credentials = json.load(file)
        
        params = {
            'client_id': credentials['spotify']['client_id'],
            'response_type': 'code',
            'redirect_uri': CALLBACK,
            'scope': "playlist-modify-private playlist-modify-public",
            'state': state,
            'code_challenge_method': 'S256',
            'code_challenge': challenge_code
        }

        server = Callback(host=HOST, port=PORT)
        server.start()
        print(f'{URL}?{urlencode(params)}')
        while server.get_key() == None:
            time.sleep(0.05)
        response_code = server.get_key()
        server.stop()

        token_body = {
            'grant_type': 'authorization_code',
            'code': response_code,
            'redirect_uri': CALLBACK,
            'client_id': credentials['spotify']['client_id'],
            'code_verifier': verifier
        }

        try:
            response = requests.post(url=TOKEN, data=token_body)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as error:
            print(f"Request Error: {error}")
        
        self.token = result['access_token']
        with open("spotify_token", "w") as file:
            file.write(self.token)
        self.id = self.get_user_id()

    
    def token_valid(self):
        ENDPOINT = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(ENDPOINT, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False

    def search(self, track:str = "", artist:str = "", album:str = "", explicit:bool = True) -> List[Track]:
        ENDPOINT = "https://api.spotify.com/v1/search"

        if not self.token_valid():
            self.new_token()

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        attempt = 0
        MAX_ATTEMPT = 2

        while True:
            if attempt > MAX_ATTEMPT:
                return None
            
            if attempt < MAX_ATTEMPT:
                track_formatted = Match.format_search(track, attempt)
                artist_formatted = Match.format_search(artist, attempt) if artist else None
                album_formatted = Match.format_search(album, 1) if album else None
                params = {
                    'q': f'{"track:" + track_formatted}{" artist:" + artist_formatted if artist else ""}{" album:" + album_formatted if album else ""}',
                    'type': 'track'
                }
            else:
                params = {
                    'q': f'{Match.format_search(track, 0)}{" " + Match.format_search(artist, 0) if artist else ""}{" " + Match.format_search(album, 0) if album else ""}',
                    'type': 'track'
                }

            try:
                response = requests.get(ENDPOINT, headers=headers, params=urlencode(params))
                response.raise_for_status()
            except requests.exceptions.RequestException as error:
                print(f"Request error: {error}")

            result = response.json()
            output = self.json_to_tracks(response.json()['tracks']['items'])
            if output != None and  len(output) > 1:
                return output

            attempt += 1
    
    def json_to_tracks(self, json_data: dict) -> List[Track]:
        if len(json_data) < 1:
            return []
        output = []
        for curr in json_data:
                if 'track' in curr:
                    curr = curr['track']
                output.append(Track(
                    id = curr['id'],
                    title = curr['name'],
                    artist = curr['artists'][0]['name'],
                    album = curr['album']['name'],
                    duration = int(curr['duration_ms'] / 1000),
                    explicit = curr['explicit'],
                    album_type = 0 if curr['album']['album_type'] == 'album' else 1 if curr['album']['album_type'] == 'single' else 2
                ))
        return output
    
    def get_playlist(self, id) -> List[Track]:
        if not self.token_valid():
            self.new_token()

        ENDPOINT = f"https://api.spotify.com/v1/playlists/{id}/tracks"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            response = requests.get(ENDPOINT, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f"Request error: {error}")

        queue = response.json()
        output = self.json_to_tracks(queue['items'])

        if not queue['total'] > queue['limit']:
            return output
        
        limit = queue['limit']
        offset = 1
        while limit * offset < queue['total']:
            params = {
                'offset': offset * limit,
                'limit': limit
            }

            try:
                response = requests.get(ENDPOINT, headers=headers, params=params)
                response.raise_for_status()
            except requests.exceptions.RequestException as error:
                print(f"Request Error: {error}")
            
            output += self.json_to_tracks(response.json()['items'])
            offset += 1

        return output
    
    def get_playlist_metadata(self, id) -> Playlist:
        if not self.token_valid():
            self.new_token()
        
        ENDPOINT = f"https://api.spotify.com/v1/playlists/{id}"
        header = {
            "Authorization": f"Bearer {self.token}"
        }

        params = {
            'limit': 200
        }
        
        try:
            response = requests.get(url=ENDPOINT, headers=header, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f"Response Error: {error}")
        
        result = response.json()

        return Playlist(result['id'], result['name'], result['description'])
    
    def new_playlist(self, title, description = "", album_cover = "") -> int | str:
        if not self.token_valid():
            self.new_token()
        
        ENDPOINT = f'https://api.spotify.com/v1/users/{self.id}/playlists'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'name': title,
            'description': description,
            'public': False
        }

        try:
            response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f'Request Error: {error}')
        
        if response.status_code == 201:
            return response.json()['id']
        else:
            print(f'Error: {self.CODES[response.status_code]}')
            return None

    def get_track(self, id) -> Track:
        if not self.token_valid():
            self.new_token()
        
        ENDPOINT = f"https://api.spotify.com/v1/tracks/{id}"
        header = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            response = requests.get(url=ENDPOINT, headers=header)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f"Request Error: {error}")
        
        result = response.json()

        return self.json_to_tracks([result])[0]
    
    def push(self, playlist_id, track_list: List[Track]):
        if len(track_list) < 1:
            print("Not pushing an empty list")
            return
        
        ENDPOINT = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

        if not self.token_valid():
            self.new_token()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        index = 0
        TOTAL = len(track_list)

        while index < TOTAL:
            read_count = 0
            uris: List[str] = []
            while read_count < 100 and index < TOTAL:
                uris.append(f'spotify:track:{track_list[index].id}')
                index += 1
                read_count += 1
                
            data = {
                'uris': uris,
                'position': 0
            }

            try:
                response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))
                response.raise_for_status()
            except requests.exceptions.RequestException as error:
                print(f'Request Error: {error}')
        
    def get_user_id(self) -> int:
        if not self.token_valid():
            self.new_token()

        ENDPOINT = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        data = None
        try:
            response = requests.get(ENDPOINT, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as error:
            print(f'Request Error: {error}')
        
        if 'id' in data:
            return int(data['id'])
        else:
            return None
        
    def remove(self, playlist_id, track_list: List[Track]):
        if not self.token_valid():
            self.new_token()
        
        ENDPOINT = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        index = 0
        TOTAL = len(track_list)
        while index < TOTAL:
            read_count = 0
            uris: List[dict] = []
            while read_count < 100 and index < TOTAL:
                uris.append({'uri': f'spotify:track:{track_list[index].id}'})
                index += 1
                read_count += 1
            data = {
                'tracks': uris
            }

            try:
                response = requests.delete(ENDPOINT, headers=headers, data=json.dumps(data))
                response.raise_for_status()
            except requests.exceptions.RequestException as error:
                print(f'Request Error: {error}')
