"""plugins/api.py

Functions to handle interacting with the Synack APIs
"""

import time
import urllib.parse
import warnings

from .base import Plugin


class Api(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Debug', 'Db']:
            setattr(self, '_'+plugin.lower(), self._registry.get(plugin)(self._state))

    @staticmethod
    def _redact(mapping):
        """Return a copy of a headers/data/query dict with secrets masked.

        Debug logging dumps request headers and bodies, which otherwise leak
        the Authorization bearer, email/password, CSRF and various Duo tokens.
        Mask anything whose key looks sensitive so logs are safe to share.
        """
        if not isinstance(mapping, dict):
            return mapping
        sensitive = ('authorization', 'cookie', 'password', 'email',
                     'csrf', 'token', 'secret', 'passcode', 'signature',
                     'akey', 'pkey', 'sid', 'xsrf')
        redacted = dict()
        for key, value in mapping.items():
            if any(s in str(key).lower() for s in sensitive):
                redacted[key] = '***REDACTED***'
            else:
                redacted[key] = value
        return redacted

    def login(self, method, path, **kwargs):
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
            base = f'https://login.{self._state.synack_domain}/api/'
        url = f'{base}{path}'
        res = self.request(method, url, **kwargs)
        return res

    def notifications(self, method, path, **kwargs):
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
            base = f'https://notifications.{self._state.synack_domain}/api/v2/'
        url = f'{base}{path}'

        if not kwargs.get('headers'):
            kwargs['headers'] = dict()
        auth = "Bearer " + self._state.notifications_token
        kwargs['headers']['Authorization'] = auth

        res = self.request(method, url, **kwargs)
        if res.status_code == 422:
            self._db.notifications_token = ''
        return res

    def request(self, method, path, attempts=0, **kwargs):
        """Send API Request

        Arguments:
        method -- Request method verb
                  (GET, POST, etc.)
        path -- API endpoint path
                Can be an endpoint on platform.synack.com or a full URL
        attempts -- Number of times the request has been attempted
        headers -- Additional headers to be added for only this request
        data -- POST body dictionary
        query -- GET query string dictionary
        """
        if path.startswith('http'):
            base = ''
        else:
            base = f'https://platform.{self._state.synack_domain}/api/'
        url = f'{base}{path}'

        # Only skip TLS verification when routing through an intercepting
        # proxy (e.g. Burp), whose CA won't be trusted. Otherwise verify
        # certificates normally.
        verify = not self._state.use_proxies
        if not verify:
            warnings.filterwarnings('ignore')

        proxies = self._state.proxies if self._state.use_proxies else None

        if f'{self._state.synack_domain}/api/' in url:
            headers = {
                'Authorization': f'Bearer {self._state.api_token}',
                'X-Synack': self._state.user_id
            }
        else:
            headers = dict()
        if kwargs.get('headers'):
            headers.update(kwargs.get('headers', {}))
        query = kwargs.get('query')
        data = kwargs.get('data')

        # No synackapi request should ever hang: cap the connect phase at 10s
        # and the read phase at 30s.
        timeout = (10, 30)

        if method.upper() == 'GET':
            res = self._state.session.get(url,
                                          headers=headers,
                                          proxies=proxies,
                                          params=query,
                                          verify=verify,
                                          timeout=timeout)
        elif method.upper() == 'HEAD':
            res = self._state.session.head(url,
                                           headers=headers,
                                           proxies=proxies,
                                           params=query,
                                           verify=verify,
                                           timeout=timeout)
        elif method.upper() == 'PATCH':
            res = self._state.session.patch(url,
                                            json=data,
                                            headers=headers,
                                            proxies=proxies,
                                            verify=verify,
                                            timeout=timeout)
        elif method.upper() == 'POST':
            if 'urlencoded' in headers.get('Content-Type', ''):
                res = self._state.session.post(url,
                                               data=data,
                                               headers=headers,
                                               proxies=proxies,
                                               verify=verify,
                                               timeout=timeout)
            else:
                res = self._state.session.post(url,
                                               json=data,
                                               headers=headers,
                                               proxies=proxies,
                                               verify=verify,
                                               timeout=timeout)
        elif method.upper() == 'PUT':
            res = self._state.session.put(url,
                                          headers=headers,
                                          proxies=proxies,
                                          params=data,
                                          verify=verify,
                                          timeout=timeout)

        # Follow any redirect the HTTP client left unresolved. requests chases
        # well-formed http(s) redirects automatically, but a 3xx with a
        # relative Location (or one it otherwise declines to follow) is handed
        # back to us as a raw 3xx -- which stalls flows like Duo that expect to
        # land on the final page. Resolve the Location against the current URL
        # and keep following until we reach a non-redirect, capping the chain
        # to avoid loops. The isinstance guard keeps mocked responses out.
        redirects = 0
        while (isinstance(res.status_code, int)
               and res.status_code in (301, 302, 303, 307, 308)
               and redirects < 20):
            location = res.headers.get('Location')
            if not location:
                break
            next_url = urllib.parse.urljoin(res.url, location)
            res = self._state.session.get(next_url,
                                          headers=headers,
                                          proxies=proxies,
                                          verify=verify,
                                          timeout=timeout)
            redirects += 1

        self._debug.log("Network Request",
                        f"{res.status_code} -- {method.upper()} -- {url}" +
                        f"\n\tHeaders: {self._redact(headers)}" +
                        f"\n\tQuery: {self._redact(query)}" +
                        f"\n\tData: {self._redact(data)}" +
                        f"\n\tContent: {res.content}")

        if res.status_code in [400, 401]:
            self._debug.log('Request failed', f'({res.status_code} - {res.reason}) {res.url}')
        elif res.status_code == 403:
            self._debug.log('Request failed', f'({res.status_code} - Logged Out) {res.url}')
        elif res.status_code == 412:
            self._debug.log('Request failed', f'({res.status_code} - Mission already claimed) {res.url}')
        elif res.status_code == 423:
            self._debug.log('Request failed', f'({res.status_code} - Locked) {res.url}')
        elif res.status_code == 429:
            self._debug.log('Too many requests', f'({res.status_code} - {res.reason}) {res.url}')
            if attempts < 5:
                self._debug.log('Pausing', 'Retrying in 30 seconds...')
                time.sleep(30)
                attempts += 1
                return self.request(method, path, attempts, **kwargs)
        elif res.status_code >= 500:
            # Only server-side (5xx) errors are worth retrying. 4xx are
            # permanent client errors -- retrying them just hammers the
            # endpoint (e.g. a 404 was being re-sent 5x during the Duo flow).
            self._debug.log('Request failed', f'({res.status_code} - {res.reason}) {res.url}')
            if attempts < 5:
                self._debug.log('Retrying', f'Attempt #{attempts + 1}')
                attempts += 1
                return self.request(method, path, attempts, **kwargs)
        elif res.status_code >= 400:
            self._debug.log('Request failed', f'({res.status_code} - {res.reason}) {res.url}')
        else:
            self._debug.log('Request Successful', f'({res.status_code} - {res.reason}) {res.url}')

        return res
