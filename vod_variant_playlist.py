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

    """
    Serialize variant manifest
    is_vod: variant type VOD or LIVE
    hls_version: hls version number
    time_offset: only applies for LIVE serving, when simulating live serving by looping current
                 data, we are serving the content in a sliding window fashion, time_offset is
                 the time since the server starts
    """
    def serialize(self, is_vod=True, hls_version=3, time_offset=0):
        playlist = "#EXTM3U\n"
        if is_vod:
            playlist += "#EXT-X-PLAYLIST-TYPE:VOD\n"
        playlist += "#EXT-X-TARGETDURATION:{}\n".format(self.target_duration)
        playlist += "#EXT-X-VERSION:{}\n".format(hls_version)
        media_sequence = 0
        start_index = 0
        if not is_vod:
            last_segment = self.segments[len(self.segments) - 1]
            total_duration = last_segment.start_time + last_segment.duration
            media_sequence += int(time_offset / total_duration) * len(self.segments)
            time_offset %= total_duration #Offset in the track that we should start serving from
            for i in range(0, len(self.segments)):
                if time_offset < (self.segments[i].start_time + self.segments[i].duration):
                    start_index = i
                    break
            media_sequence += start_index
        playlist += "#EXT-X-MEDIA-SEQUENCE:{}\n".format(media_sequence)
        segments = self.segments[start_index:] + self.segments[:start_index]
        for s in segments:
            playlist += "#EXTINF:{},\n".format(s.duration)
            playlist += "{}\n".format(s.location)
            if s.discontinuity:
                playlist += "#EXT-X-DISCONTINUITY\n"
        # If VOD, put #EXT-X-ENDLIST instead of discontinuity tag
        if is_vod:
            playlist = playlist[:playlist.rfind("#EXT-X-DISCONTINUITY\n")]
            playlist += "#EXT-X-ENDLIST\n"
        return playlist


    """
    Concatenate a new variant playlist after the current one
    The new playlist needs to have the exact same parameters (bandwidth,
    resolution, codecs, target segment length.
    """
    def concatenate(self, new_playlist):
        if new_playlist.bandwidth != self.bandwidth or \
           new_playlist.resolution != self.resolution or \
           new_playlist.codecs != self.codecs or \
           new_playlist.target_duration != self.target_duration:
               raise RuntimeError("Cannot append variant playlist"\
                       "different parameters detected")
        index = len(self.segments)
        start_time = self.segments[index - 1].start_time + \
                     self.segments[index - 1].duration
        for s in new_playlist.segments:
            s.id = index
            s.start_time = start_time
            self.segments.append(s)
            index += 1
            start_time += s.duration
