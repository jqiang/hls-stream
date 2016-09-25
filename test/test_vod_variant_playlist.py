import unittest
import vod_variant_playlist as playlist

class VodVariantPlaylistTestCase(unittest.TestCase):
    def setUp(self):
        # Successful creation
        self.playlist = playlist.VodVariantPlaylist(206400,
                "568x320", "avc1.42001f, mp4a.40.2",
                "testdata/m1-1-1000000/index.m3u8")

    def test_create_non_existing_file(self):
        # Non existing segment location
        with self.assertRaises(FileNotFoundError):
            playlist.VodVariantPlaylist(206400,
                "568x320", "avc1.42001f, mp4a.40.2",
                "testdata/m1-1-9999999/index.m3u8")

    def test_parse(self):
        self.assertEqual(self.playlist.target_duration, 9)
        # Check segment 0
        segment = self.playlist.segments[0]
        self.assertEqual(segment.id, 0)
        self.assertEqual(segment.location, "testdata/m1-1-1000000/frag-1.ts")
        self.assertEqual(segment.start_time, 0)
        self.assertEqual(segment.duration, 9)
        self.assertEqual(segment.discontinuity, False)
        # Check segment 1
        segment = self.playlist.segments[1]
        self.assertEqual(segment.id, 1)
        self.assertEqual(segment.location, "testdata/m1-1-1000000/frag-2.ts")
        self.assertEqual(segment.start_time, 9)
        self.assertEqual(segment.duration, 9)
        self.assertEqual(segment.discontinuity, False)
        # Check segment 5
        segment = self.playlist.segments[5]
        self.assertEqual(segment.id, 5)
        self.assertEqual(segment.location, "testdata/m1-1-1000000/frag-6.ts")
        self.assertEqual(segment.start_time, 45)
        self.assertEqual(segment.duration, 9)
        self.assertEqual(segment.discontinuity, False)
        # Check last segment (10)
        segment = self.playlist.segments[10]
        self.assertEqual(segment.id, 10)
        self.assertEqual(segment.location, "testdata/m1-1-1000000/frag-11.ts")
        self.assertEqual(segment.start_time, 90)
        self.assertEqual(segment.duration, 4)
        self.assertEqual(segment.discontinuity, True)

    def test_serialize_vod(self):
        with open("test/expected/test_variant_expected", "r") as f:
            expected = f.read()
            self.assertEqual(self.playlist.serialize(True, 3), expected)

    def test_serialize_live(self):
        self.maxDiff = None
        with open("test/expected/test_variant_live_expected", "r") as f:
            expected = f.read()
            self.assertEqual(self.playlist.serialize(False, 3,31), expected)

    def test_concatenate(self):
        new_playlist = playlist.VodVariantPlaylist(206400,
                "568x320", "avc1.42001f, mp4a.40.2",
                "testdata/m2-1-1000000/index.m3u8")
        self.playlist.concatenate(new_playlist)
        with open("test/expected/test_variant_concatenated_expected", "r") as f:
            expected = f.read()
            self.assertEqual(self.playlist.serialize(True, 3), expected)

if __name__ == '__main__':
    unittest.main()
