import logging
import requests

class YoutubeAPIHandler:

    @staticmethod
    def make_api_request(*args, **kwargs):
        """
        Makes an API request using specified arguments. Involves the API link combined with criteria specifying what is to be requested

       :return: The JSON response from the API if the request is successful; otherwise, None.

       Logs an error and returns `None` if an exception occurs during the request (e.g., connection issues).
   """
        try:
            response = requests.get(*args, **kwargs)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Fehler bei der API-Anfrage: {e}")
            return None