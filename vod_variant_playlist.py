"""
Contains information from one single VOD variant playlist
Which should include general information:
    bandwidth, resolution, codec
As well as a list of media segments included in this track
"""

import os
import segment
import re

class VodVariantPlaylist():
    def __init__(self, bandwidth, resolution, codecs, location):
        self.bandwidth = bandwidth
        self.resolution = resolution
        self.codecs = codecs
        if os.path.isfile(location):
            self.target_duration, self.segments = self.parse(location)
        else:
            raise FileNotFoundError("Unable to find {}".format(location))

    def parse(self, location):
        with open(location, 'r') as f:
            content = f.read()

        pattern = r"^#EXT-X-TARGETDURATION:(?P<target_duration>\d+)$"
        match = re.search(pattern, content, re.M)
        if match is None:
            raise RuntimeError("Unable to find target duration")
        target_duration = int(match.group("target_duration"))
        path = os.path.dirname(location)
        segments = []
        segment_index = 0
        segment_start_time = 0
        # Regex parsing, output will be iteration object with "duration" and "location"
        # for each segment
        pattern = r"^#EXTINF:(?P<duration>\d+),[^ ](?P<location>.*?\.ts)$"
        for match in re.finditer(pattern, content, re.M):
            segment_duration = int(match.group("duration"))
            segment_location = os.path.join(path, match.group("location"))
            # Validate that file exists at location
            if not os.path.isfile(segment_location):
                raise FileNotFoundError("Unable to find {}".format(location))
            s = segment.Segment(segment_index, segment_location, segment_start_time, segment_duration)
            segments.append(s)
            segment_index += 1
            segment_start_time += segment_duration
        # Let's set discontinuity flag on last segment
        last_segment = segments[segment_index-1]
        last_segment.update_discontinuity(True)
        return (target_duration, segments)

    def serialize(self, is_vod=True, hls_version=3):
        playlist = "#EXTM3U\n"
        if is_vod:
            playlist += "#EXT-X-PLAYLIST-TYPE:VOD\n"
        playlist += "#EXT-X-TARGETDURATION:{}\n".format(self.target_duration)
        playlist += "#EXT-X-VERSION:{}\n".format(hls_version)
        for s in self.segments:
            playlist += "#EXTINF:{},\n".format(s.duration)
            playlist += "{}\n".format(s.location)
            if s.discontinuity:
                playlist += "#EXT-X-DISCONTINUITY\n"
        # If VOD, put #EXT-X-ENDLIST instead of discontinuity tag
        if is_vod:
            playlist = playlist[:playlist.rfind("#EXT-X-DISCONTINUITY\n")]
            playlist += "#EXT-X-ENDLIST\n"
        return playlist
