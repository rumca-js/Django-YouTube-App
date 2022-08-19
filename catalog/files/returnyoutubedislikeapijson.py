import logging
import json


class YouTubeThumbsDown(object):
    
    def __init__(self, data):
        self.loads(data)

    def read_code_data(self, code):
        url = "https://returnyoutubedislikeapi.com/votes?videoId="+code

        data = basictypes.get_page(url)
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
    
    def get_likes(self):
        return self._json['likes']
    
    def get_dislikes(self):
        return self._json['dislikes']
    
    def get_view_count(self):
        return self._json['viewCount']
    
    def get_rating(self):
        return self._json['rating']
