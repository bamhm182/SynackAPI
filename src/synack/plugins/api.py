"""plugins/api.py

Functions to handle interacting with the Synack APIs
"""

import warnings
import requests


class Api:
    def __init__(self, handler):
        self.handler = handler
        self.session = None

        self.build_session()

    def build_session(self):
        self.session = requests.Session()
        if self.handler.db.api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.handler.db.api_token}',
            })

    def login(self, method, path,
              headers=None, data=None, query=None):
        """Modify API Request for Login

        Arguments:
        method -- Request method verb
                  (GET, POST, etc.)
        path -- API endpoint path
                Can be an endpoint on platform.synack.com or a full URL
        headers -- Additional headers to be added for only this request
        data -- POST body dictionary
        query -- GET query string dictionary
        """
        if path.startswith('http'):
            base = ''
        else:
            base = 'https://login.synack.com/api/'
        url = f'{base}{path}'
        res = self.request(method, url, headers, data, query)
        return res

    def notifications(self, method, path,
                      headers=None, data=None, query=None):
        """Modify API Request for Notifications

        Arguments:
        method -- Request method verb
                  (GET, POST, etc.)
        path -- API endpoint path
                Can be an endpoint on platform.synack.com or a full URL
        headers -- Additional headers to be added for only this request
        data -- POST body dictionary
        query -- GET query string dictionary
        """
        if path.startswith('http'):
            base = ''
        else:
            base = 'https://notifications.synack.com/api/v2/'
        url = f'{base}{path}'

        if not self.handler.db.notifications_token:
            self.handler.auth.get_notifications_token()

        if not headers:
            headers = dict()
        auth = "Bearer " + self.handler.db.notifications_token
        headers['Authorization'] = auth

        res = self.request(method, url, headers, data, query)
        if res.status_code == 422:
            self.handler.db.notifications_token = ""
        return res

    def request(self, method, path, headers=None, data=None, query=None):
        """Send API Request

        Arguments:
        method -- Request method verb
                  (GET, POST, etc.)
        path -- API endpoint path
                Can be an endpoint on platform.synack.com or a full URL
        headers -- Additional headers to be added for only this request
        data -- POST body dictionary
        query -- GET query string dictionary
        """
        if path.startswith('http'):
            base = ''
        else:
            base = 'https://platform.synack.com/api/'
        url = f'{base}{path}'

        if self.handler.db.use_proxies:
            warnings.filterwarnings("ignore")
            verify = False
            proxies = self.handler.db.proxies
        else:
            verify = True
            proxies = None

        if method.upper() == 'GET':
            res = self.session.get(url,
                                   headers=headers,
                                   proxies=proxies,
                                   params=query,
                                   verify=verify)
        elif method.upper() == 'HEAD':
            res = self.session.head(url,
                                    headers=headers,
                                    proxies=proxies,
                                    params=query,
                                    verify=verify)
        elif method.upper() == 'PATCH':
            res = self.session.patch(url,
                                     json=data,
                                     headers=headers,
                                     proxies=proxies,
                                     verify=verify)
        elif method.upper() == 'POST':
            res = self.session.post(url,
                                    json=data,
                                    headers=headers,
                                    proxies=proxies,
                                    verify=verify)

        self.handler.debug.log("Network Request",
                               f"{res.status_code} -- {url} -- {res.content}")

        return res
