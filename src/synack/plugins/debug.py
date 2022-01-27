"""plugins/debug.py

Defines the methods to increase verbosity and aid in debugging
"""

from datetime import datetime

class Debug:
    def __init__(self, handler, enabled):
        self.handler = handler
        self.enabled = enabled

    def log(self, title, message, level="DEBUG"):
        if self.enabled:
            t = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            print(f'{t} -- {title.upper()}\n\t{message}')
