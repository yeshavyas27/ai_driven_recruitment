from app import logging_utilities


class BaseRouter:
    def __init__(self):
        self.logger = logging_utilities.logger