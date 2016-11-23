#!/usr/bin/env python3

import http.server
import socketserver
import os
import socket
import time
import re
import argparse
import vod_master_playlist as mp

global master_playlist
global start_time
global is_vod

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def send_head(self):
        """Serve a GET request."""
        path = self.translate_path(self.path)
        """Handle requests for listing directory"""
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        file_name = os.path.basename(path)
        f = None
        try:
            content_type = ""
            # We don't support directory listing
            if os.path.isdir(path):
                raise Exception("Illegal url of directory type")
            # If request media segment, return it
            if file_name.endswith(".ts"):
                content_type = "video/mp2t"
            # If request master playlist, return it (it's already prepared
            if self.path == "/playlist.m3u8":
                content_type = "application/vnd.apple.mpegurl"
            # If request variant playlist, we need to generate it
            match = re.match(r"/index-(?P<variant_index>\d+).m3u8", self.path)
            if match:
                generate_variant_playlist(int(match.group("variant_index")))
                content_type = "application/vnd.apple.mpegurl"
            if not content_type:
                raise Exception("Illegal url")
            # Now create the header
            f = open(path, 'rb')
            content_length = str(os.fstat(f.fileno())[6])
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Content-Length", content_length)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
        except IOError as e:
            # 404 File Not found
            self.send_error(404, e)
        except Exception as e:
            # 500 internal server error
            self.send_error(500, e)
        return f

def generate_master_playlist(source_playlists):
    global master_playlist
    master_playlist = mp.VodMasterPlaylist(source_playlists[0])
    for p in source_playlists[1:]:
        new_playlist = mp.VodMasterPlaylist(p)
        master_playlist.concatenate(new_playlist)
    f = open("playlist.m3u8", 'w')
    f.write(master_playlist.serialize())
    f.close()

def generate_variant_playlist(variant_index):
    if variant_index < 0 or variant_index > (len(master_playlist.variants) - 1):
        raise IOError("Non existing variant playlist")
    if master_playlist is None:
        raise Exception("Master playlist has not been initialized")
    f = open("index-{}.m3u8".format(variant_index), 'w')
    time_offset = 0
    if not is_vod:
        time_offset = int(time.time()) - start_time
    f.write(master_playlist.variants[variant_index].serialize(is_vod, 3, time_offset))
    f.close()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    return s.getsockname()[0]

def main():
    # Parse the arguments
    help_text = """
    Start HLS streaming server with existing hls vod files
    You can serve either single VOD file, or concatenat several VOD files and serve them (They must be with same
    encoding parameters to be concatenated)
    You can also start live streaming by looping existing vod file(s) with -l or --loop
    """
    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument('playlists', metavar='playlists', type=str, nargs='+',
            help="List of source playlists to serve from, orders or playlists will be following during serving")
    parser.add_argument('-p', '--port', nargs='?', type=int, default=8000,
            help="Port to serve from, default 8000")
    parser.add_argument('-l', '--loop', dest='loop', action='store_true',
            help="Serve in loop mode (live streaming)")
    args = parser.parse_args()
    source_playlists = args.playlists
    port = args.port
    global is_vod
    is_vod = (not args.loop)
    # Prepare master playlist
    generate_master_playlist(source_playlists)
    # Start timecode
    global start_time
    start_time = int(time.time())
    # Start webserver
    Handler = CustomHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    print("Watch stream at: http://{}:{}/playlist.m3u8".format(get_ip_address(), port))
    httpd.serve_forever()

if __name__ == '__main__':
    main()
