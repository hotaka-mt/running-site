import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from running_ocr.value_parser import parse_value
from running_ocr.layouts.mi_fitness import MI_FITNESS_LAYOUT

TEXTS = ['5.25', '2026/10/0518:30', '00:32:15', '350 kcal', '400 kcal', '6\'09"', '145 BPM', '5200']
EXPECTED = dict(zip(MI_FITNESS_LAYOUT['basic']['fields'], [5.25, datetime(2026, 10, 5, 18, 30, tzinfo=ZoneInfo('Asia/Tokyo')), 1935, 350, 400, 369, 145, 5200]))


class ValueParserTests(unittest.TestCase):
    def test_eight_values(self):
        for (key, field), text in zip(MI_FITNESS_LAYOUT['basic']['fields'].items(), TEXTS):
            self.assertEqual(parse_value(text, field), EXPECTED[key])

    def test_invalid_values(self):
        for key, text in [('datetime', '2026/02/3018:30'), ('duration', '00:60:00'), ('avg_pace', '6\'60"'), ('steps', '歩数'), ('distance_km', '-1'), ('avg_bpm', '145 kcal')]:
            self.assertIsNone(parse_value(text, MI_FITNESS_LAYOUT['basic']['fields'][key]))
        self.assertEqual(parse_value(' 145 bpm ', MI_FITNESS_LAYOUT['basic']['fields']['avg_bpm']), 145)
