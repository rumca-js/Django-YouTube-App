from django.db import models
from django.urls import reverse


class VideoLinkDataModel(models.Model):

    url = models.TextField(max_length=1000, help_text='url')
    artist = models.TextField(max_length=1000, help_text='artist')
    album = models.TextField(max_length=1000, help_text='album')
    title = models.TextField(max_length=1000, help_text='title')
    category = models.TextField(max_length=1000, help_text='category')
    subcategory = models.TextField(max_length=1000, help_text='subcategory')
    tag = models.TextField(max_length=1000, help_text='tag')

    class Meta:
        ordering = ['artist', 'album', 'title']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('link-detail', args=[str(self.id)])

    def get_video_code(self):
        return VideoLinkDataModel.input2code(self.url)

    def input2url(item):
        code = YouTubeLinkBasic.input2code(item)
        return YouTubeLinkBasic.code2url(code)

    def code2url(code):
        return 'https://www.youtube.com/watch?v={0}'.format(code)

    def input2code(url):
        wh = url.find("=")
        if wh == -1:
            wh = url.find("youtu.be")
            if wh == -1:
                video_code = url
            else:
                video_code = url[wh+9:]
        else:
            wh2 = url.find("&")
            if wh2 != -1:
                video_code = url[wh+1:wh2]
            else:
                video_code = url[wh+1:]
        return video_code

    def get_embed_link(self):
        return "https://www.youtube.com/embed/{0}".format(self.get_video_code() )

    def __str__(self):
        return "{0}/{1}".format(self.title, self.url)


class YouTubeLinkBasic(VideoLinkDataModel):

    def __init__(self, link):
        super().__init__()
        self.init_for_link(link)
        self.url = link

    def init_for_link(self, link):
        self._video_code = ""
        self.process_input(link)

    def get_video_code(self):
        return self._video_code

    def process_input(self, link):
        self._video_code = YouTubeLinkBasic.input2code(link)
        self.url = YouTubeLinkBasic.code2url(self._video_code)

    def input2url(item):
        code = YouTubeLinkBasic.input2code(item)
        return YouTubeLinkBasic.code2url(code)

    def code2url(code):
        return 'https://www.youtube.com/watch?v={0}'.format(code)

    def input2code(url):
        wh = url.find("=")
        if wh == -1:
            wh = url.find("youtu.be")
            if wh == -1:
                video_code = url
            else:
                video_code = url[wh+9:]
        else:
            wh2 = url.find("&")
            if wh2 != -1:
                video_code = url[wh+1:wh2]
            else:
                video_code = url[wh+1:]
        return video_code

    def get_embed_link(self):
        return "https://www.youtube.com/embed/{0}".format(self.get_video_code() )


class VideoChannelDataModel(models.Model):

    url = models.TextField(max_length=1000, help_text='url')
    artist = models.TextField(max_length=1000, help_text='artist', default="")
    album = models.TextField(max_length=1000, help_text='album', default="")
    title = models.TextField(max_length=1000, help_text='title', default="")
    category = models.TextField(max_length=1000, help_text='category', default="")
    subcategory = models.TextField(max_length=1000, help_text='subcategory', default="")
    tag = models.TextField(max_length=1000, help_text='tag', default="")

    class Meta:
        ordering = ['title']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('channel-detail', args=[str(self.id)])


class YouTubeChannelBasic(VideoChannelDataModel):

    def __init__(self, link):
        self.init_for_link(link)

    def init_for_link(self, link, data = None):
        self._chan_code = ""
        self.init_data(data)
        self.process_input(link)

    def process_input(self, link):
        self._chan_code = YouTubeChannelBasic.input2code(link)
        self.set_url(YouTubeChannelBasic.code2url(self._chan_code))

    def input2code(input_data):
        if input_data.find("https://www.youtube.com/channel/") >= 0:
            wh = input_data.rfind("channel/")
            _chan_code = input_data[wh+8:]
        elif input_data.find("https://www.youtube.com/feeds/videos.xml?channel_id=") >= 0:
            wh = input_data.rfind("channel_id=")
            _chan_code = input_data[wh+11:]
        else:
            _chan_code = input_data

        wh2 = _chan_code.find("&")
        if wh2 != -1:
            _chan_code = _chan_code[:wh2]

        return _chan_code

    def input2url(input_data):
        code = YouTubeChannelBasic.input2code(input2code)
        return YouTubeChannelBasic.code2url(code)

    def code2url(code):
        return "https://www.youtube.com/channel/"+code

    def code2rssurl(code):
        return "https://www.youtube.com/feeds/videos.xml?channel_id="+code

    def get_channel_code(self):
        return self._chan_code 
