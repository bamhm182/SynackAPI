"""test_Transactions.py

Tests for the _Transactions.py Transactions Class
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock


class TransactionsTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        self.transactions = synack.Transactions(synack.Handler())

    def test_get_balance(self):
        """Should get the balance of your synack account"""
        bal = b'''{
            "total_balance": "10.0",
            "pending_payout": "0.0"
        }'''
        self.transactions.handler.api.request.return_value.headers = {'x-balance':bal}
        self.transactions.handler.api.request.return_value.status_code = 200
        ret = self.transactions.get_balance()
        self.assertEqual(ret, json.loads(bal))
        self.transactions.handler.api.request.assert_called_with('HEAD', 'transactions')
