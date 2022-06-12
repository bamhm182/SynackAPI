"""test_templates.py

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

    def test_build_filepath_from_mission(self):
        """Should return path from mission json"""
        self.templates.build_safe_name = MagicMock()
        self.templates.build_safe_name.side_effect = [
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
                         self.templates.build_filepath(mission))

    def test_build_filepath_from_evidences(self):
        """Should return path from evidences json"""
        self.templates.build_safe_name = MagicMock()
        self.templates.build_safe_name.side_effect = [
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
                         self.templates.build_filepath(mission))

    def test_build_sections(self):
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
            ret = self.templates.build_sections('/tmp/mission.txt')
            self.assertEqual(sections, ret)
            m.assert_called_with('/tmp/mission.txt', 'r')

    def test_get_file(self):
        self.templates.build_filepath = MagicMock()
        self.templates.build_filepath.return_value = '/tmp/mission.txt'
        self.templates.build_sections = MagicMock()
        sections = {
            "section1": "Section 1 text"
        }
        mission = {
            "placeholder": "Placeholder"
        }
        self.templates.build_sections.return_value = sections
        with patch.object(pathlib.Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            self.templates.get_file(mission)
            self.templates.build_filepath.assert_called_with(mission)
            self.templates.build_sections.assert_called_with('/tmp/mission.txt')

    def test_set_file(self):
        self.templates.build_filepath = MagicMock()
        self.templates.build_filepath.return_value = '/tmp/mission.txt'
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
                                 self.templates.set_file(template))
                m.assert_called_with('/tmp/mission.txt', 'w')
                m.return_value.write.assert_called_with(out)

    def test_build_safe_name(self):
        """Should convert complex missions names to something simpler"""
        one = self.templates.build_safe_name("S!oME_RaNdOm___MISSION!")
        one_out = "s_ome_random_mission_"
        self.assertEqual(one_out, one)
