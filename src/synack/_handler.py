"""handler.py

Defines the handler class and generally sets up the project.
"""

import importlib

from ._state import State
from synack.plugins.base import Plugin

class Handler:
    def __init__(self, state=State(), **kwargs):
        self.state = state
        
        for key in kwargs.keys():
            if hasattr(self.state, key):
                setattr(self.state, key, kwargs.get(key))

        for name, subclass in Plugin.registry.items():
            instance = subclass(self.state)
            setattr(self, name.lower(), instance)

        if self.state.login and not self.auth.check_api_token():
            self.auth.get_api_token()
