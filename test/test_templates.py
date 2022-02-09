"""test_templates.py"

Tests for the Templates Plugin
"""

import os
import sys
import unittest
import pathlib

from unittest.mock import MagicMock, mock_open, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class TemplatesTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.templates = synack.plugins.Templates(self.state)
        self.templates.db = MagicMock()

    def test_get_template_path_from_mission(self):
        """Should return path from mission json"""
        self.templates.do_convert_name = MagicMock()
        self.templates.do_convert_name.side_effect = [
            'mission',
            'web',
            'mission'
        ]
        mission = {
            'taskType': 'MISSION',
            'assetTypes': [
                'Web'
            ],
            'title': 'Mission'
        }
        self.templates.db.template_dir = pathlib.Path('/tmp')
        self.assertEqual('/tmp/mission/web/mission.txt',
                         self.templates.get_template_path(mission))

    def test_get_template_path_from_evidences(self):
        """Should return path from evidences json"""
        self.templates.do_convert_name = MagicMock()
        self.templates.do_convert_name.side_effect = [
            'mission',
            'web',
            'mission'
        ]
        mission = {
            'taskType': 'MISSION',
            'asset': 'web',
            'title': 'Mission'
        }
        self.templates.db.template_dir = pathlib.Path('/tmp')
        self.assertEqual('/tmp/mission/web/mission.txt',
                         self.templates.get_template_path(mission))

    def test_get_sections_from_file(self):
        m = mock_open()
        m.return_value.read.return_value = '''
        [[[section1]]]
        Section 1 text

        [[[section2]]]

        Section 2 text

        [[[END]]]
        '''
        sections = {
            "section1": "Section 1 text",
            "section2": "Section 2 text"
        }
        with patch('builtins.open', m, create=True):
            ret = self.templates.get_sections_from_file('/tmp/mission.txt')
            self.assertEqual(sections, ret)
            m.assert_called_with('/tmp/mission.txt', 'r')

    def test_get_template(self):
        self.templates.get_template_path = MagicMock()
        self.templates.get_template_path.return_value = '/tmp/mission.txt'
        self.templates.get_sections_from_file = MagicMock()
        sections = {
            "section1": "Section 1 text"
        }
        mission = {
            "placeholder": "Placeholder"
        }
        self.templates.get_sections_from_file.return_value = sections
        with patch.object(pathlib.Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            self.templates.get_template(mission)
            self.templates.get_template_path.assert_called_with(mission)
            self.templates.get_sections_from_file.\
                assert_called_with('/tmp/mission.txt')

    def test_do_save_template(self):
        self.templates.get_template_path = MagicMock()
        self.templates.get_template_path.return_value = '/tmp/mission.txt'
        template = {
            "version": "2",
            "structuredResponse": "Structured Response",
            "introduction": "Introduction",
            "testing_methodology": "Testing Methodology",
            "conclusion": "Conclusion"
        }
        m = mock_open()
        out = "\n".join([
            "[[[structuredResponse]]]\n",
            template["structuredResponse"],
            "\n[[[introduction]]]\n",
            "THIS IS A DOWNLOADED TEMPLATE!",
            "ENSURE THERE IS NO SENSITIVE INFORMATION,",
            "THEN DELETE THIS WARNING!\n",
            template["introduction"],
            "\n[[[testing_methodology]]]\n",
            template["testing_methodology"],
            "\n[[[conclusion]]]\n",
            template["conclusion"],
            "\n[[[END]]]"
        ])

        with patch('builtins.open', m, create=True):
            with patch.object(pathlib.Path, 'exists') as mock_exists:
                mock_exists.return_value = False
                self.assertEqual('/tmp/mission.txt',
                                 self.templates.do_save_template(template))
                m.assert_called_with('/tmp/mission.txt', 'w')
                m.return_value.write.assert_called_with(out)

    def test_do_convert_name(self):
        """Should convert complex missions names to something simpler"""
        one = self.templates.do_convert_name("S!oME_RaNdOm___MISSION!")
        one_out = "s_ome_random_mission_"
        self.assertEqual(one_out, one)
