"""plugins/transactions.py

Functions dealing with payouts/money
"""

import json

from .base import Plugin


class Transactions(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def get_balance(self):
        """Get your current account balance and requested payout values"""
        res = self.api.request('HEAD', 'transactions')
        if res.status_code == 200:
            return json.loads(res.headers.get('x-balance'))
