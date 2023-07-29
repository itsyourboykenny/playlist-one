from providers import *
import xmltodict

# See providers.py for documentation

class LastFM(Provider):
    def __init__(self) -> None:
        self.ENDPOINT = 'http://ws.audioscrobbler.com/2.0/'
        self.token = None
        try:
            with open('lastfm_token', 'r') as file:
                self.token = file.read()
        except FileNotFoundError:
            self.token = None

    def new_token(self) -> str:
        with open('credentials.json', 'r') as file:
            credentials = json.load(file)['lastfm']
        
        print(f'http://www.last.fm/api/auth/?api_key={credentials["client_id"]}')
        server = Callback()
        server.start()
        while not server.get_key():
            time.sleep(0.05)
        auth_key = server.get_key()
        server.stop()

        response: requests.Response = self.call(
            url = 'http://ws.audioscrobbler.com/2.0/',
            method = 'get',
            params = {
                'method': 'auth.getSession',
                'api_key': credentials['client_id'],
                'token': auth_key,
                'api_sig': hashlib.md5(f'api_key{credentials["client_id"]}methodauth.getSessiontoken{auth_key}{credentials["client_secret"]}'.encode()).hexdigest()
            }
        )
        content = xmltodict.parse(response.content)
        self.token = content['lfm']['session']['key']

        with open('lastfm_token', 'w') as file:
            file.write(self.token)
    
    def search(self, track:str, artist:str = None, album:str = None, explicit:bool = True) -> List[Track]:
        credential = None
        try:
            with open('credentials.json', 'r') as file:
                credential = json.load(file)['lastfm']
        except FileNotFoundError as error:
            raise error
        
        params = {
            'method': 'track.getInfo',
            'track': track,
            # 'limit': 10,
            'api_key': credential['client_id'],
            'format': 'json',
            'autocorrect': 1
        }
        if artist:
            params['artist'] = artist

        response: dict = self.call(
            url = self.ENDPOINT,
            params = urlencode(params)
        ).json()
        
        return [Track(
            title = response['track']['name'],
            artist = response['track']['artist']['name'],
            duration = response['track']['duration']
        )]
    
    def json_to_tracks(self, json_data: dict) -> List[Track]:
        output: List[Track] = []
        if len(json_data['results']['trackmatches']['track']) < 1:
            return output
        
        # try:
        #     with open('credentials.json', 'r') as file:
        #         credential = json.load(file)['lastfm']
        # except FileNotFoundError as error:
        #     raise error

        for track in json_data['results']['trackmatches']['track']:
            # info: dict = self.call(
            #     url = self.ENDPOINT,
            #     method = 'get',
            #     params = urlencode({
            #         'method': 'track.getInfo'
            #     })
            # )
            output.append(
                Track(
                    title=track['name'],
                    artist=track['artist']
                )
            )


test = LastFM()
test.search(track='Put It On Da Floor Again (feat. Cardi B)', artist='latto')