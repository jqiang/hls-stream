import unittest
import segment

class SegmentTestCase(unittest.TestCase):
    def setUp(self):
        # Succesful creation
        self.segment = segment.Segment(0,
                "testdata/m1-1-1000000/frag-10.ts",
                0, 9, False)

    def test_create_non_existing_file(self):
        # Non existing segment location
        with self.assertRaises(FileNotFoundError):
            segment.Segment(0,
                "testdata/m1-1-1000000/frag-100.ts",
                0, 9, False)

    def test_serialize(self):
        expected = "#EXTINF:9,\ntestdata/m1-1-1000000/frag-10.ts\n"
        self.assertEqual(self.segment.serialize(), expected)

if __name__ == '__main__':
    unittest.main()
