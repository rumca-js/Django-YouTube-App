import logging
import json


def get_page(url):
    import urllib.request, urllib.error, urllib.parse
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webContent = urllib.request.urlopen(req).read().decode('UTF-8')
        return webContent
    except Exception as e:
       logging.critical(e, exc_info=True)


class YouTubeThumbsDown(object):
    
    def __init__(self, link = None):
        self._link = link

    def download_data(self):
        return YouTubeThumbsDown.read_code_data(self._link.get_video_code())

    def read_code_data(code):
        url = "https://returnyoutubedislikeapi.com/votes?videoId="+code

        data = get_page(url)
        return data

    def loads(self, data):
        try:
            self._json = json.loads(data)
            return self._json
        except Exception as e:
            logging.critical(e, exc_info=True)
            self._json = {}

    def get_json(self):
        return self._json
    
    def get_thumbs_up(self):
        return self._json['likes']
    
    def get_thumbs_down(self):
        return self._json['dislikes']
    
    def get_view_count(self):
        return self._json['viewCount']
    
    def get_rating(self):
        return self._json['rating']
