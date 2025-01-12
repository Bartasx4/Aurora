import time


class Clock:
    """
    Represents a clock event scheduler managing timed execution of events.

    The Clock class provides functionalities to add, schedule, execute, and remove
    events. Events are identified by unique integers and are associated with
    callback functions and delays. The clock tracks events internally using a
    dictionary. Users can also retrieve the current Unix timestamp via the `now`
    property.

    :ivar events: A dictionary storing scheduled events. Keys are integers
        representing event IDs, and values are dictionaries containing event
        details such as the callback function, next execution time, and delay.
    :type events: dict[int, dict[str, any]]
    """
    EVENT_TIMER_FIELD_NAMES = ['timer', 'function', 'delay']

    def __init__(self):
        self.events: dict[int, dict[str, any]] = {}

    def add(self, event: int, callback: callable, delay: int) -> None:
        """
        Adds an event to the event scheduler. The event is associated with a specific
        callback function to be executed after a defined delay.

        :param event: The identifier for the event to add.
        :param callback: The function to be executed when the event occurs.
        :param delay: The delay in seconds before the event is triggered.

        :return: None
        """
        next_execution_time = self._calculate_next_execution_time(delay)
        self.events[event] = {
            'timer': next_execution_time,
            'function': callback,
            'delay': delay
        }

    def set(self, event: int, delay: int) -> None:
        """
        Sets an event with a specific delay, calculating its next execution time and updating
        the event details accordingly in the internal events dictionary.

        :param event: The identifier for the event to be scheduled.
        :param delay: The delay in seconds after which the event should be triggered.

        :returns: None
        """
        next_execution_time = self._calculate_next_execution_time(delay)
        self.events[event]['delay'] = delay
        self.events[event]['timer'] = next_execution_time

    def make_step(self) -> dict[int, any]:
        """
        Executes scheduled events if their timers expired and updates their timers.

        This method iterates through the scheduled events dictionary. If the event's
        execution time has been reached or passed, it executes the associated callback
        function. The timer for the event is then updated by adding the delay interval.
        Results of executed events (if any) are collected and returned.

        :returns:
            A dictionary where keys are event IDs and values are the results of
            executed callback functions.
        :rtype: dict[int, any]
        """
        results = {}
        current_time = self.now

        for event_id, event_data in self.events.items():
            next_execution_time = event_data['timer']
            callback = event_data['function']
            delay = event_data['delay']

            if 0 < next_execution_time < current_time:
                results[event_id] = callback()
                event_data['timer'] = current_time + delay

        return results

    @property
    def now(self) -> int:
        """
        Provides the current Unix timestamp.

        The `now` property retrieves the current time as a Unix timestamp,
        represented as an integer. This timestamp represents the number of seconds
        that have elapsed since 00:00:00 UTC on 1 January 1970.

        :return: The current Unix timestamp as an integer.
        """
        return int(time.time())

    def remove(self, event: int) -> None:
        """
        Removes an event from the tracked events dictionary. This method attempts to
        remove the specified event by its key from the internal storage. If the
        specified key is not present, no changes will be made, and no error will
        be raised.

        :param event: The key of the event to be removed from the internal events
            dictionary.

        :return: None
        """
        self.events.pop(event, None)

    def _calculate_next_execution_time(self, delay: int) -> int:
        """
        Calculate and return the next execution time based on the given delay.

        This method computes the next execution timestamp by adding the specified
        delay to the current time (`self.now`). If the delay is non-positive, it
        defaults to returning 0.

        :param delay: The delay in seconds to calculate the next execution time.

        :return: The calculated timestamp for the next execution or 0 if the delay
            is non-positive.
        """
        return self.now + delay if delay > 0 else 0
