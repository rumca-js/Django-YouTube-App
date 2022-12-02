from django.db import models
from django.urls import reverse
import logging


class VideoLinkDataModel(models.Model):

    url = models.CharField(max_length=1000, unique=True)
    artist = models.CharField(max_length=1000)
    album = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    category = models.CharField(max_length=1000)
    subcategory = models.CharField(max_length=1000)
    tag = models.CharField(max_length=1000)

    class Meta:
        ordering = ['artist', 'album', 'title']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('catalog:link-detail', args=[str(self.id)])

    def get_video_code(self):
        return VideoLinkDataModel.input2code(self.url)

    def input2url(item):
        code = VideoLinkDataModel.input2code(item)
        return VideoLinkDataModel.code2url(code)

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

    def get_thumbnail(self):
        y = YouTubeLinkComposite(self.url)
        return y.get_thumbnail()


class VideoLinkDetailsDataModel(models.Model):

    url = models.CharField(max_length=1000, help_text='url', unique=True)
    details_json = models.CharField(max_length=1000, help_text='details_json')
    dead = models.BooleanField(default = False, help_text='dead')

class VideoLinkReturnDislikeDataModel(models.Model):
    url = models.CharField(max_length=1000, help_text='url', unique=True)
    return_dislike_json = models.CharField(max_length=1000, help_text='return_dislike_json')
    dead = models.BooleanField(default = False, help_text='dead')


class YouTubeLinkComposite(object):

    def __init__(self, url = None):
        self._json = None
        self._thumbs = None

        if url:
            self.url = url
            self.get_details()

    def get_video_code(self):
        return VideoLinkDataModel.input2code(self.url)

    def get_details(self):
        from .prjconfig import Configuration

        d = VideoLinkDetailsDataModel.objects.filter(url=self.url)
        r = VideoLinkReturnDislikeDataModel.objects.filter(url=self.url)

        if not d.exists() or not r.exists():
            pass
        else:
            if not d[0].dead:
                from .files.youtubelinkjson import YouTubeJson
                self._json = YouTubeJson()
                if not self._json.loads(d[0].details_json):
                    logging.error("Could not read json for {0}, removing details data".format(self.url))
                    d.delete()

            if not r[0].dead:
                from .files.returnyoutubedislikeapijson import YouTubeThumbsDown
                self._thumbs = YouTubeThumbsDown()
                if not self._thumbs.loads(r[0].return_dislike_json):
                    logging.error("Could not read json for {0}, removing returndislike api data".format(self.url))
                    r.delete()

    def has_details(self):
        from .prjconfig import Configuration

        d = VideoLinkDetailsDataModel.objects.filter(url=self.url)
        r = VideoLinkReturnDislikeDataModel.objects.filter(url=self.url)

        if not d.exists() or not r.exists():
            return False

        return True

    def get_description(self):
        if self._json:
            return self._json.get_description()

    def get_thumbnail(self):
        if self._json:
            return self._json.get_thumbnail()

    def get_upload_date(self):
        if self._json:
            return self._json.get_upload_date()

    def get_view_count(self):
        if self._thumbs:
            return self._thumbs.get_view_count()

    def get_thumbs_up(self):
        if self._thumbs:
            return self._thumbs.get_thumbs_up()

    def get_thumbs_down(self):
        if self._thumbs:
            return self._thumbs.get_thumbs_down()

    def get_dead(self):
        d = VideoLinkDetailsDataModel.objects.filter(url=self.url)
        r = VideoLinkReturnDislikeDataModel.objects.filter(url=self.url)

        dead = False
        if d.exists():
            if d[0].dead:
                dead = True
        if r.exists():
            if r[0].dead:
                dead = True

        return dead

    def request_details_download(self):
        from .prjconfig import Configuration

        from . import views
        app_name = str(views.app_name)

        c = Configuration.get_object(str(app_name))
        c.download_link_details(self)

    def download_details(self):
      from .programwrappers import ytdlp
      from .files.returnyoutubedislikeapijson import YouTubeThumbsDown

      d = VideoLinkDetailsDataModel.objects.filter(url=self.url)
      if not d.exists():
        yt = ytdlp.YTDLP(self.url)
        json = yt.download_data()

        if json:
            details_record = VideoLinkDetailsDataModel(url=self.url,
                                               details_json = json)
            details_record.save()
        else:
            details_record = VideoLinkDetailsDataModel(url=self.url,
                                               details_json = "",
                                               dead = True)
            details_record.save()

      r = VideoLinkReturnDislikeDataModel.objects.filter(url=self.url)
      if not r.exists():
        ytr = YouTubeThumbsDown(self)
        return_json = ytr.download_data()

        if return_json:
            return_record = VideoLinkReturnDislikeDataModel(url=self.url,
                                               return_dislike_json = return_json)

            return_record.save()
        else:
            return_record = VideoLinkReturnDislikeDataModel(url=self.url,
                                               return_dislike_json = "",
                                               dead = True)

            return_record.save()

    def reset(self):
      logging.info("Ressing information about: "+self.url)

      d = VideoLinkDetailsDataModel.objects.filter(url=self.url)
      if d.exists():
          if d[0].dead:
              d[0].dead = False
              d[0].save()

      r = VideoLinkReturnDislikeDataModel.objects.filter(url=self.url)
      if r.exists():
          if r[0].dead:
              r[0].dead = False
              r[0].save()


class VideoChannelDataModel(models.Model):

    url = models.CharField(max_length=1000, unique=True)
    artist = models.CharField(max_length=1000, default="")
    album = models.CharField(max_length=1000, default="")
    title = models.CharField(max_length=1000, default="")
    category = models.CharField(max_length=1000, default="")
    subcategory = models.CharField(max_length=1000, default="")
    tag = models.CharField(max_length=1000, default="")

    class Meta:
        ordering = ['title']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('catalog:channel-detail', args=[str(self.id)])


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
