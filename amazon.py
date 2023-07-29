from providers import *

class Amazon:
    def __init__(self) -> None:
        self.token: str = None

        try:
            with open('amazon_token', 'r') as file:
                self.token = file.read()
        except FileNotFoundError as error:
            self.token = None

    def new_token(self):
        try:
            with open("./credentials.json", "r") as file:
                credentials = json.load(file)
        except FileNotFoundError as error:
            print("Credential file is missing")
        
        ENDPOINT = "https://api.amazon.com/auth/o2/create/codepair"
        ID = credentials['amazon']['client_id']
        SECRET = credentials['amazon']['client_secret']
        REDIRECT = 'http://localhost:9999/callback'
        TOKEN = 'https://api.amazon.com/auth/o2/token'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        params = {
            'response_type': 'device_code',
            'client_id': ID,
            'scope': 'profile'#'amazon_music:access'
        }

        response = requests.post(url=ENDPOINT, headers=headers, data=params)
        result = response.json()
        print(result['verification_uri'])

        cred = {
            'grant_type': 'device_code',
            'device_code': result['device_code'],
            'user_code': result['user_code']
        }
        token = requests.post(url=TOKEN, headers=headers, data=cred)
        result = token.json()

        with open('amazon_token', 'w') as file:
            file.write(result['access_token'])

    def search(self, track:str, artist:str = "", album:str = "", explicit:bool = True) -> List[Track]:
        ENDPONT = 'https://music-api.amazon.com/search/'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            'keywords': track
        }

        response = requests.get(url=ENDPONT, params=params, headers=headers)
        result = response.json()
        print(result)