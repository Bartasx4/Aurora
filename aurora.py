import json
import time
import datetime
import requests
from clock import Clock

# Constants
PUSH_URL = 'https://api.pushover.net:443/1/messages.json'
AURORA_URL = 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'
K_INDEX_URL = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
SECOND, MINUTE, HOUR = 1, 60, 3600
SEND_DELAY, SEND_DELAY_DAY = HOUR, 4 * HOUR
CHECK_DELAY = MINUTE
START_DAY, END_DAY = datetime.time(6, 0), datetime.time(19, 0)
CHECK_EVENT = 1
RESET_EVENT = 2
AURORA_LEVELS = {
    'pl': [
        (90, 'Lokalnie: 90. Masz ją nad głową!'),
        (80, 'Lokalnie: 80. Ogromna szansa!'),
        (70, 'Lokalnie: 70. Bardzo duża szansa.'),
        (50, 'Lokalnie: 50. Może coś się pojawi. Wypatruj.'),
        (30, 'Lokalnie: 30. Jeżeli będziesz mieć bardzo dużo szczęścia')
    ],
    'en': [
        (90, 'Locally: 90. You have it on your head!'),
        (80, 'Locally: 80. Very likely!'),
        (70, 'Locally: 70. Very likely.'),
        (50, 'Locally: 50. Something might happen. Take a break.'),
        (30, 'Locally: 30. If you have a lot of happiness')]
}
K_INDEX_LEVELS = {
    'pl': [
        (9, 'Globalnie: 9. Musisz ją widzieć!'),
        (8, 'Globalnie: 8. Duża szansa!'),
        (7, 'Globalnie: 7. Dzisiaj jest spora szansa.'),
        (6, 'Globalnie: 6. Dzisiaj jest szansa.'),
        (5, 'Globalnie: 5. Jakaś tam szansa dzisiaj jest.')
    ],
    'en': [
        (9, 'Globally: 9. You have to see it!'),
        (8, 'Globally: 8. Very likely!'),
        (7, 'Globally: 7. There is a lot of chance today.'),
        (6, 'Globally: 6. There is a chance today.'),
        (5, 'Globally: 5. There might be a chance today.')
    ]
}
HEADERS = {'Content-type': 'application/x-www-form-urlencoded'}


class Aurora:
    """
    Class responsible for monitoring and notifying about aurora and geomagnetic activity levels.

    This class integrates with external APIs to collect data regarding auroral
    activations and K-index levels. It processes this data, evaluates activity levels,
    and sends push notifications when thresholds are surpassed. Additionally, it operates
    in a loop to periodically check for activity updates and manage daytime-based delays.

    :ivar api_key: API key used for authentication with the Push notification service.
    :type api_key: str
    :ivar user_key: User key associated with the recipient of push notifications.
    :type user_key: str
    :ivar latitude: Latitude coordinate for the location to monitor aurora activity.
    :type latitude: int
    :ivar longitude: Longitude coordinate for the location to monitor aurora activity.
    :type longitude: int
    :ivar language: Language used for notification messages. Default is 'pl'.
    :type language: str
    :ivar clock: Instance for scheduling and managing periodic tasks.
    :type clock: Clock
    :ivar is_day: Indicates whether the current time is within daytime hours.
    :type is_day: bool
    :ivar last_send_time: Timestamp of the last sent push notification.
    :type last_send_time: int
    :ivar last_k_level: Last K-index level of geomagnetic activity recorded.
    :type last_k_level: int
    :ivar last_aurora_level: Last aurora activity level recorded.
    :type last_aurora_level: int
    """
    def __init__(self, api_key: str, user_key: str, latitude: int, longitude: int, language: str = 'pl'):
        self.api_key = api_key
        self.user_key = user_key
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
        self.clock = Clock()
        self.is_day = False
        self.last_send_time = 0
        self.last_k_level = 0
        self.last_aurora_level = 0

    def update_daytime_delay(self):
        """
        Updates the delay for daytime events based on the current daytime status.

        This method checks if the current state of `is_day` is consistent with
        `is_daytime`. If they are different, it updates `is_day` to match
        `is_daytime` and sets an appropriate delay for resetting an event. The
        delay is determined by whether it is daytime or not, using predefined
        constants `SEND_DELAY_DAY` for daytime and `SEND_DELAY` for non-daytime.

        :raises ValueError: If the method fails to update the clock with an invalid
                            or undefined delay.

        """
        if self.is_daytime != self.is_day:
            self.is_day = self.is_daytime
            delay = SEND_DELAY_DAY if self.is_day else SEND_DELAY
            self.clock.set(RESET_EVENT, delay)

    def check(self):
        """
        Evaluates aurora and K-index levels, logs the results, and sends a push notification
        if necessary.

        This method checks the current aurora level and K-index level, compares them with the
        previous recorded levels, and logs the relevant information. If a significant change
        or condition is detected, it generates a notification message and sends it.

        :raises: This method does not raise any specific exception.
        :return: A notification message containing updates on aurora or K-index levels if
            there are significant changes, or an empty string if no updates are relevant.
        :rtype: str
        """
        print(f'{time.strftime("%H:%M")}; ', end='')
        aurora_result = self._evaluate_aurora_level()
        k_index_result = self._evaluate_k_index_level()
        print(f'last aurora: {self.last_aurora_level}; last k-index: {self.last_k_level}; day: {self.is_day}')
        message = '\n'.join(filter(None, [aurora_result, k_index_result]))
        if message:
            self.send_push(message)
        return message

    def _evaluate_aurora_level(self) -> str | None:
        """
        Evaluates the aurora activity level for the configured location and retrieves its
        corresponding descriptive message. The method calculates the local aurora activity
        by processing downloaded aurora data, fetching the aurora intensity for the configured
        longitude and latitude, and comparing it against the maximum auroral intensity found
        in the dataset.

        :raises KeyError: Raised if the expected keys are not found in processed aurora data.
        :raises ValueError: Raised if aurora levels are improperly configured or invalid.

        :return: A descriptive message indicating the current aurora level compared to
                 predefined thresholds. Returns None if no meaningful data is available.
        :rtype: str | None
        """
        coordinates = self._process_aurora_data(self._download_aurora_data())
        local_level = coordinates.get((self.longitude, self.latitude), 0)
        max_aurora = max(coordinates.values())
        print(f'Aurora: {local_level}; Max Aurora: {max_aurora}; ', end='')
        return self._get_message_from_levels(local_level, AURORA_LEVELS[self.language], 'last_aurora_level')

    def _evaluate_k_index_level(self) -> str | None:
        """
        Evaluates the K-index level based on retrieved data and returns the respective
        message indicating the quality level (Preliminary, Provisional, Definitive).
        The K-index is used to quantify disturbances in the Earth's magnetic field
        and provides insight into geomagnetic conditions. Data is downloaded and
        processed, returning a categorized message based on predefined levels.

        :return: A message string corresponding to the K-index quality level or None
            if the evaluation fails.
        :rtype: str | None
        """
        # - "P" - Preliminary (Wstępny): Wstępne dane, mogą zostać zaktualizowane.
        # - "M" - Provisional (Provisional): Tymczasowe dane, bardziej dokładne niż wstępne, ale nadal podlegające rewizji.
        # - "Z" - Definitive (Ostateczny): Ostateczne, zatwierdzone dane, uznawane za najbardziej dokładne.
        k_time, k_index = self._download_k_index_data()
        print(f'k-index: {k_index:.1f}; k-time: {k_time}; ', end='')
        return self._get_message_from_levels(k_index, K_INDEX_LEVELS[self.language], 'last_k_level')

    def _get_message_from_levels(self, current_value: float | int, thresholds: tuple[int, str], last_level_var: str) -> str | None:
        """
        Determines the appropriate message based on the current value and threshold levels. The function
        compares the `current_value` against each level in the `thresholds` tuple while also checking
        and updating the `last_level_var` stored in the object. If the `current_value` matches the
        condition for any specific level, the associated message is returned. If no levels match, the
        function returns `None`.

        :param current_value:
            The current numerical value to evaluate, which is compared against the thresholds.
        :param thresholds:
            A tuple where each element is a pair containing a numerical level and a corresponding
            string message.
        :param last_level_var:
            The attribute name within the object storing the previously crossed threshold level. This
            value is updated if a new threshold level is crossed.
        :return:
            A string message if the current value crosses a new threshold level. Returns `None` if no
            threshold is crossed.
        """
        for level, message in thresholds:
            if current_value >= level > getattr(self, last_level_var):
                setattr(self, last_level_var, level)
                return message
        return None

    @staticmethod
    def _download_aurora_data():
        response = requests.get(AURORA_URL)
        if response.ok:
            return response.json()
        raise ConnectionError(f'Error downloading aurora data: {response.status_code}, {response.content}')

    @staticmethod
    def _download_k_index_data():
        """
        Downloads the latest K-index data from a predefined URL and extracts the most
        recent time tag and Kp index value. The function performs a GET request to fetch
        data and processes the response, ensuring that it retrieves valid information.

        :raises ConnectionError: If the HTTP request fails or the response is invalid.

        :return: A tuple containing the most recent `time_tag` as a formatted string
            and the corresponding `kp_index` as a float.
        :rtype: tuple[str, float]
        """
        response = requests.get(K_INDEX_URL)
        if response.ok:
            data = response.json()[-1]
            k_time = data.get('time_tag', '').replace('T', ' ')
            k_index = data.get('kp_index', 0.0)
            return k_time, k_index
        raise ConnectionError(f'Error downloading K-index data: {response.status_code}, {response.content}')

    @property
    def is_daytime(self):
        """
        Determines if the current time falls within the defined daytime range.

        This property checks if the current time is within the predefined
        `START_DAY` and `END_DAY` time boundaries. Daytime is specified by
        these global time constants.

        :return: A boolean value indicating whether the current time is within
            the daytime range.
        :rtype: bool
        """
        current_time = datetime.datetime.now().time()
        return START_DAY <= current_time <= END_DAY

    @staticmethod
    def _process_aurora_data(data: json):
        """
        Processes aurora data from the provided JSON format into a sorted dictionary.

        This method extracts `coordinates` data from the JSON input and maps it into a dictionary where the
        keys are tuples of longitude and latitude, and the values are the corresponding aurora values.
        The resulting dictionary is then sorted based on the keys.

        :param data: A JSON object containing aurora data with 'coordinates' as a key. The value of
                     'coordinates' is expected to be a list of tuples, where each tuple consists of
                     longitude, latitude, and aurora values.
        :type data: json

        :return: A sorted dictionary where keys are tuples of longitude and latitude, and values
                 are the aurora values.
        :rtype: dict

        :raises ValueError: If the `coordinates` data is unavailable or empty in the provided JSON.
        """
        coordinates = {(lon, lat): aurora for lon, lat, aurora in data.get('coordinates', [])}
        if not coordinates:
            raise ValueError("No aurora data available.")
        return dict(sorted(coordinates.items()))

    def reset(self):
        """Reset tracked aurora and K-index levels."""
        self.last_aurora_level = 0
        self.last_k_level = 0

    def send_push(self, message: str):
        """
        Sends a push notification message to the specified user using configured API credentials.

        This method constructs a payload containing the API key, user key, and the notification
        message to send it via an HTTP POST request. The required headers and content type
        are included in the request. If the message is successfully sent, the time of the last
        successful send is updated. If the request fails, a `ConnectionError` is raised with
        the response's status code and content.

        :param message: The message to be sent as the push notification.

        :return: The HTTP response object from the push notification API request, if the notification
                 has been sent successfully.
        :rtype: requests.Response
        :raises ConnectionError: If the request to the push notification API fails, the response status
                                 code and content are included in the exception.
        """
        payload = {
            'token': self.api_key,
            'user': self.user_key,
            'message': message,
            'Content-type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(PUSH_URL, headers=HEADERS, data=payload)
        if response.ok:
            self.last_send_time = self.clock.now
            return response
        raise ConnectionError(response.status_code, response.content)

    def start_loop(self):
        """
        Initiates the main loop for orchestrating and managing periodic events. This method
        uses a clock to schedule recurring events, such as checking and resetting processes,
        while dynamically updating the delay based on the time of day. The loop continues
        indefinitely, ensuring that all events are executed in a defined sequence and at
        appropriate intervals.

        :param self: Represents the instance of the class.
        :return: None
        """
        self.clock.add(CHECK_EVENT, self.check, CHECK_DELAY)
        self.clock.add(RESET_EVENT, self.reset, SEND_DELAY)
        self.update_daytime_delay()
        self.check()
        while True:
            self.clock.make_step()
            self.update_daytime_delay()
            time.sleep(3)
