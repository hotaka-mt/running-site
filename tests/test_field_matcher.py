import unittest
from running_ocr.field_matcher import resolve_regions, get_region_key
from running_ocr.layouts.mi_fitness import MI_FITNESS_LAYOUT


class FieldMatcherTests(unittest.TestCase):
    def test_partition_and_boundaries(self):
        regions = resolve_regions((310, 456, 3), MI_FITNESS_LAYOUT['basic']['fields'])
        for y in range(310):
            for x in range(456):
                self.assertEqual(sum(a <= x < c and b <= y < d for a, b, c, d in regions.values()), 1)
        self.assertEqual(get_region_key(208, 0, regions), 'datetime')
        self.assertEqual(get_region_key(122, 133, regions), 'active_kcal')
        self.assertEqual(get_region_key(247, 215, regions), 'steps')
        self.assertIsNone(get_region_key(456, 0, regions))

    def test_invalid_partitions(self):
        for fields in [
            {'a': {'region': (0, 0, 6, None)}, 'b': {'region': (5, 0, None, None)}},
            {'a': {'region': (0, 0, 4, None)}, 'b': {'region': (5, 0, None, None)}},
            {'a': {'region': (0, 0, 11, None)}},
        ]:
            with self.assertRaises(ValueError):
                resolve_regions((10, 10), fields)
