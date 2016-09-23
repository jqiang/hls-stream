import unittest
import vod_master_playlist as playlist

class VodMasterPlaylistTestCase(unittest.TestCase):
    def setUp(self):
        self.playlist = playlist.VodMasterPlaylist(
                "testdata/m1-all_Custom.m3u8")

    def test_parse(self):
        # Check number of variants
        self.assertEqual(len(self.playlist.variants), 1)
        # Check that parameters are parsed correctly
        variant = self.playlist.variants[0]
        self.assertEqual(variant.bandwidth, 2064000)
        self.assertEqual(variant.resolution, "568x320")
        self.assertEqual(variant.codecs, {"avc1.42001f", "mp4a.40.2"})
        self.assertEqual(len(variant.segments), 11)

if __name__ == '__main__':
    unittest.main()
