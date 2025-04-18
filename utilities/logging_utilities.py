import logging
import os
from datetime import datetime
from typing import Any


class LoggingUtilities:
    def __init__(self):
        # debug settings
        debug = os.getenv("DEBUG")
        
        # Create a custom logger for your app instead of configuring the root logger
        self.logger = logging.getLogger("fastapi_app")
        
        # Prevent adding duplicate handlers
        if not self.logger.handlers:
            # Set the level for your logger
            self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
            
            # Define log format
            log_format = '%(levelname)s: [%(asctime)s] [%(pathname)s:%(lineno)d] [%(module)s] [%(funcName)s] [%(name)s] %(message)s'
            formatter = logging.Formatter(log_format)
            
            # Create handlers
            if not debug:
                os.makedirs('/app/logs', exist_ok=True)  # Create logs directory if it doesn't exist
                file_handler = logging.FileHandler(f'/app/logs/{datetime.now().strftime("%m-%d-%Y")}.log')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            else:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
        
        # Prevent propagation to the root logger
        self.logger.propagate = False
        
    def get_logger(self):
        return self.logger