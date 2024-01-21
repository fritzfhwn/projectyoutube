import logging
import requests

class YoutubeAPIHandler:

    @staticmethod
    def make_api_request(*args, **kwargs):
        try:
            response = requests.get(*args, **kwargs)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Fehler bei der API-Anfrage: {e}")
            return None