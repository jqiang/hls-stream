"""
   Segment class is simulating a segment in segment table for streaming server
   Segment table will look like:
   | id | location | start_time | duration | discontinuity |
"""

import os.path

class Segment():
    def __init__(self, id, location, start_time, duration, discontinuity=False):
        self.id = id
        if os.path.isfile(location):
            self.location = location
        else:
            raise FileNotFoundError("Unable to find {}".format(location))
        self.start_time = start_time
        self.duration = duration
        self.discontinuity = discontinuity

    def update_discontinuity(self, discontinuity):
        self.discontinuity = discontinuity

    def serialize(self):
        return "#EXTINF:{},\n{}\n".format(self.duration, self.location)
