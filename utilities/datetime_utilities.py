class DatetimeUtilities:

    @staticmethod
    def get_delta_in_milliseconds(datetime_1, datetime_2):

        # Calculate the difference between the two datetime
        delta = datetime_2 - datetime_1
        # Convert the difference to milliseconds and return the absolute value
        return abs(delta.total_seconds() * 1000)