import os
from aurora import Aurora


USER_KEY = os.getenv('USER_KEY')
API_KEY = os.getenv('API_KEY')

LATITUDE = 60
LONGITUDE = 18
LANGUAGE = 'pl'


def initialize_aurora_monitor(api_key: str, user_key: str, latitude: int, longitude: int, language: str) -> Aurora:
    """
    Initialize the Aurora monitoring service with the provided configuration.
    """
    return Aurora(api_key, user_key, latitude, longitude, language)


if __name__ == '__main__':
    aurora_monitor = initialize_aurora_monitor(API_KEY, USER_KEY, LATITUDE, LONGITUDE, LANGUAGE)
    try:
        aurora_monitor.start_loop()
    except KeyboardInterrupt:
        exit()
