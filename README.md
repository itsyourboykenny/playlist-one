# playlist-one
Multi-provider playlist sync tool. Fully sandboxed and runs locally to only your machine. You are required to have your own developer account and supply your own `client_id`/`client_secret`. Currently only Spotify and Deezer have full support. Apple music will be added once it makes sense for me to pay for a developer account by them. To add providers you will create a class which 'inherits' `providers.py`, define it's methods and be imported to `pl1.py`.
## Usage
`python3 pl1.py --src {provider} --dest {provider} --toid {id} --fromid {id} --method {method}`  
- Provider:
  - `spotify`
  - `deezer`
- Methods:
  - `mirror`
  - `merge`
- Options:
  - `--src`: Source provider
  - `--dest`: Destination provider
  - `--toid`: Destination playlist ID
  - `--fromid`: Source playlist ID
  - `--method`: Sync method
