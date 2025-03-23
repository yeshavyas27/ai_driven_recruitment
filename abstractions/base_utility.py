from app import logging_utilities


class BaseUtility:
    def __init__(self):
        self.logger = logging_utilities.logger