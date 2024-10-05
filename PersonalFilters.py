from telegram.ext.filters import MessageFilter


class PersonalFilters(MessageFilter):
    """
        Filter for messages from a specific user.

        :param message: The message to check.

        :return: True if the message has the filter, False otherwise.

    """

    def filter(self, message):
        # Add personal filter logic here
        pass

