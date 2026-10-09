import json
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

from running_ocr.field_matcher import resolve_regions
from running_ocr.layouts.mi_fitness import MI_FITNESS_LAYOUT
from running_ocr.pipeline import extract_running_data


class MiFitnessRegressionTests(unittest.TestCase):
    def test_recorded_screenshots(self):
        # 実画像3枚の OCR 結果を再生し、目視確認済みの値と比較する。
        fixtures = json.loads((Path(__file__).parent / 'fixtures/mi_fitness_ocr.json').read_text())
        for filename, fixture in fixtures.items():
            with self.subTest(filename=filename):
                names = iter(name for name, section in MI_FITNESS_LAYOUT.items() if section['fields'])
                class RecordedEngine:
                    def predict(self, image, **options):
                        section = next(names)
                        if options != MI_FITNESS_LAYOUT[section].get('ocr_options', {}):
                            raise AssertionError(options)
                        start, end = MI_FITNESS_LAYOUT[section]['crop']
                        if image.shape != (end - start, 397, 3):
                            raise AssertionError(image.shape)
                        return fixture['detections'][section]
                expected = fixture['expected']
                expected['basic']['datetime'] = datetime.fromisoformat(expected['basic']['datetime'])
                actual = extract_running_data(np.zeros((3680, 397, 3), dtype=np.uint8),
                                              MI_FITNESS_LAYOUT, RecordedEngine())
                self.assertEqual(actual, expected)
                self.assertNotIn('chart', actual['bpm'])
                self.assertNotIn('map', actual)

    def test_all_partitions(self):
        for name, section in MI_FITNESS_LAYOUT.items():
            if name == 'map':
                continue
            with self.subTest(section=name):
                start, end = section['crop']
                regions = resolve_regions((end - start, 397, 3), section['fields'])
                coverage = np.zeros((end - start, 397), dtype=np.uint8)
                for x1, y1, x2, y2 in regions.values():
                    coverage[y1:y2, x1:x2] += 1
                self.assertTrue(np.all(coverage == 1))
