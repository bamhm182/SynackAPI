"""plugins/transactions.py

Functions dealing with payouts/money
"""

import json

from .base import Plugin


class Transactions(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Auth']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def get_balance(self):
        """Get your current account balance and requested payout values"""
        res = self._api.request('HEAD', 'transactions')
        if res.status_code == 200:
            return json.loads(res.headers.get('x-balance'))
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()

    def get(self, period='', max_pages=1, page=1, per_page=15, **kwargs):
        query = {
            'period': period,
            'per_page': per_page,
            'page': page
        }

        res = self._api.request('GET',
                                'transactions',
                                query=query)

        if res.status_code == 200:
            ret = res.json()
            if len(ret) == per_page and page < max_pages:
                new = self.get(period=period,
                               max_pages=max_pages,
                               page=page+1,
                               per_page=per_page)
                ret.extend(new)
            return ret
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()
        return []
