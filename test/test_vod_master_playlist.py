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

    def test_serialize(self):
        expected = "#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1," \
        "BANDWIDTH=2064000,RESOLUTION=568x320,CODECS=\"avc1.42001f, mp4a.40.2\"\n" \
        "index-0.m3u8\n"
        self.assertEqual(self.playlist.serialize(), expected)

    def test_concatenate(self):
        new_playlist = playlist.VodMasterPlaylist(
                "testdata/m2-all_Custom.m3u8")
        self.playlist.concatenate(new_playlist)

        # Check concatenated master playlist
        expected = "#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1," \
        "BANDWIDTH=2064000,RESOLUTION=568x320,CODECS=\"avc1.42001f, mp4a.40.2\"\n" \
        "index-0.m3u8\n"
        self.assertEqual(self.playlist.serialize(), expected)

        # Check concatenate variant playlist
        with open("test/expected/test_variant_concatenated_expected", "r") as f:
            expected = f.read()
            self.assertEqual(self.playlist.variants[0].serialize(True, 3), expected)

if __name__ == '__main__':
    unittest.main()
