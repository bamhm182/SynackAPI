"""test_utils.py

Tests for the plugins/utils.py Utils class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.state._db = MagicMock()
        self.utils = synack.plugins.Utils(self.state)

    def test_get_html_tag_value(self):
        """Should return value when name comes before content/value in the tag"""
        html = '<input type="hidden" name="csrf" value="abc123"/>'
        self.assertEqual('abc123', self.utils.get_html_tag_value('csrf', html))

    def test_get_html_tag_value_no_match(self):
        """Should return empty string when the field is not found"""
        html = '<input type="hidden" name="other" value="abc123"/>'
        self.assertEqual('', self.utils.get_html_tag_value('csrf', html))

    def test_get_html_tag_value_reversed(self):
        """Should return value when content/value comes before name in the tag"""
        html = '<meta content="abc123" name="csrf"/>'
        self.assertEqual('abc123', self.utils.get_html_tag_value('csrf', html))
