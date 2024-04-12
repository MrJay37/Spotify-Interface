import requests
import base64
import json


class SpotifyAPIInterface:
    _BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

    def _get_access_token(self):
        try:
            with open('access_token.json') as f:
                access_token = f.read()
                f.close()

        except FileNotFoundError:
            return self._refresh_access_token()

        access_token = json.loads(access_token)

        return access_token['access_token']

    def _refresh_access_token(self):
        auth = base64.b64encode(bytes(self._client_id + ':' + self._client_secret, 'utf-8')).decode('utf-8')

        res = requests.post(
            url='https://accounts.spotify.com/api/token',
            headers={
                'Authorization': 'Basic ' + auth,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'client_credentials'
            }
        )

        data = res.json()

        with open('access_token.json', 'w') as f:
            f.write(json.dumps(data))
            f.close()

        return data['access_token']

    def call(self, resource, method='GET', body=None, params=None):
        res = requests.request(
            url=self._BASE_URL + resource,
            method=method,
            data=body,
            params=params,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self._get_access_token()
            }
        )

        if res.status_code == 401:
            message = res.json()['error']['message']

            if message == 'The access token expired':
                self._refresh_access_token()
                return self.call(resource, method, body, params)

        return res

    def get_artist(self, artist_id):
        artist = self.call('/artists/' + artist_id)

        return artist.json()

    def get_artists_related_artists(self, artist_id):
        res = self.call(f"/artists/{artist_id}/related-artists")

        return res.json()
