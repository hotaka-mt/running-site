import unittest
from unittest.mock import patch
import numpy as np
from running_ocr.ocr_engine import OCREngine
from running_ocr.pipeline import extract_region, extract_running_data
from running_ocr.image_splitter import crop_image
from running_ocr.layouts.mi_fitness import MI_FITNESS_LAYOUT
from test_value_parser import TEXTS, EXPECTED


class FakeBackend:
    def __init__(self):
        self.calls = 0

    def predict(self, image):
        self.calls += 1
        return [{'rec_texts': TEXTS + ['距離', '9.99', 'bad'],
                 'rec_scores': [.9] * 8 + [1., .2, 1.],
                 'rec_boxes': [(10, 10, 20, 20), (210, 10, 220, 20), (10, 140, 20, 150),
                               (130, 140, 140, 150), (250, 140, 260, 150), (10, 220, 20, 230),
                               (110, 220, 120, 230), (250, 220, 260, 230)] + [(10, 10, 20, 20)] * 3}]


class PipelineTests(unittest.TestCase):
    def test_windows_and_numeric_selection(self):
        class Engine:
            def predict(self, image):
                return [{'text': '平均心拍数', 'score': 1., 'center': (1, 1)},
                        {'text': '175', 'score': .9, 'center': (1, 1)}]
        section = {'crop': (0, 10), 'fields': {
            'value': {'region': (0, 0, None, None), 'parser': 'int'}}}
        layout = {'first': section, 'second': {**section, 'numeric_only': False}}
        with patch('running_ocr.utils.image_window_manager.show_detections') as show:
            data = extract_running_data(np.zeros((10, 10)), layout, Engine(), window_manager=object())
        self.assertEqual(data, {'first': {'value': 175}, 'second': {'value': 175}})
        self.assertEqual([call.args[3] for call in show.call_args_list], ['ocr_first', 'ocr_second'])
        self.assertEqual([item['text'] for item in show.call_args_list[0].args[1]], ['175'])
        self.assertEqual([item['text'] for item in show.call_args_list[1].args[1]], ['平均心拍数', '175'])

    def test_ocr_options(self):
        backend = unittest.mock.Mock()
        backend.predict.return_value = []
        engine = OCREngine(backend)
        image = np.zeros((10, 10))
        section = {'fields': {'value': {'region': (0, 0, None, None), 'parser': 'int'}},
                   'ocr_options': {'use_doc_orientation_classify': False}}
        self.assertEqual(extract_region(image, section, engine), {'value': None})
        backend.predict.assert_called_once_with(image, use_doc_orientation_classify=False)

    def test_eight_fields_and_model_reuse(self):
        backend = FakeBackend()
        engine = OCREngine(backend)
        image = np.zeros((915, 456, 3), dtype=np.uint8)
        for _ in range(2):
            self.assertEqual(extract_running_data(image, MI_FITNESS_LAYOUT, engine, sections=['basic']), {'basic': EXPECTED})
        self.assertEqual(backend.calls, 2)
        self.assertEqual([detection['text'] for detection in engine.predict(image)], TEXTS + ['距離', '9.99', 'bad'])

    def test_custom_layout_and_missing_values(self):
        class Engine:
            def predict(self, image):
                return [{'text': '42', 'score': .8, 'center': (1, 1)}]
        layout = {'other': {'crop': (None, None), 'fields': {
            'custom': {'region': (0, 0, 5, None), 'parser': 'int'},
            'missing': {'region': (5, 0, None, None), 'parser': 'float'}}}}
        self.assertEqual(extract_running_data(np.zeros((10, 10)), layout, Engine()),
                         {'other': {'custom': 42, 'missing': None}})
        self.assertEqual(extract_region(np.zeros((10, 10)), {'fields': {}}, Engine()), {})

    def test_invalid_crop(self):
        with self.assertRaises(ValueError):
            crop_image(np.zeros((10, 10)), (5, 11))
