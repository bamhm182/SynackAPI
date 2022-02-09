"""factories.py

Factories to create various things as necessary
"""


class ObjectFactory:
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs.get(k))
