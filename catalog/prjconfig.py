from pathlib import Path
import logging

from .threads import *
from .programwrappers import ytdlp
from .basictypes import *

from .models import YouTubeLinkComposite

__version__ = "0.1.2"


class Configuration(object):
   obj = None

   def __init__(self, app_name):
       self.app_name = app_name
       self.directory = Path("/home/rumpel/WorkDir/DjangoPage/linklibrary")
       self.version = __version__

       self.enable_logging()
       self.create_threads()

   def get_object(app_name):
       app_name = str(app_name)
       if not Configuration.obj:
           Configuration.obj = {app_name : Configuration(app_name)}
       if app_name not in Configuration.obj:
           Configuration.obj[app_name] = Configuration(app_name)

       return Configuration.obj[app_name]

   def enable_logging(self, create_file = True):
       self.server_log_file = self.directory / "log_{0}.txt".format(self.app_name)
       self.global_log_file = self.directory / "log_global.txt"

       logging.shutdown()

       self.global_log_file.unlink(True)
       self.server_log_file.unlink(True)

       logging.basicConfig(level=logging.INFO, filename=self.global_log_file, format='[%(asctime)s %(name)s]%(levelname)s:%(message)s')

       # create logger for prd_ci
       log = logging.getLogger(self.app_name)
       log.setLevel(level=logging.INFO)

       # create formatter and add it to the handlers
       formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

       if create_file:
               # create file handler for logger.
               fh = logging.FileHandler(self.server_log_file)
               fh.setLevel(level=logging.DEBUG)
               fh.setFormatter(formatter)
       # reate console handler for logger.
       ch = logging.StreamHandler()
       ch.setLevel(level=logging.DEBUG)
       ch.setFormatter(formatter)

       # add handlers to logger.
       if create_file:
           log.addHandler(fh)

       log.addHandler(ch)
       return  log 

   def create_threads(self):
       download_music_thread = ThreadJobCommon("download-music")
       download_video_thread = ThreadJobCommon("download-video")
       link_details_thread = ThreadJobCommon("download-link-details")
       channel_details_thread = ThreadJobCommon("download-channel-details")
       refresh_thread = ThreadJobCommon("refresh-thread", 3600, True) #3600 is 1 hour

       self.threads = [
               download_music_thread,
               download_video_thread,
               link_details_thread,
               channel_details_thread,
               refresh_thread
               ]

       for athread in self.threads:
           athread.set_config(self)
           athread.start()

   def close(self):
       for athread in self.threads:
           athread.close()

   def get_threads(self):
      return self.threads

   def t_process_item(self, thread, item):
      if thread == "download-music":
         self.t_download_music(item)
      elif thread == "download-video":
         self.t_download_video(item)
      elif thread == "download-link-details":
         self.t_download_link_details(item)
      elif thread == "download-channel-details":
         self.t_download_channel_details(item)
      elif thread == "refresh-thread":
         self.t_refresh(item)
      else:
         raise NotImplemented

   def t_download_music(self, item):
      log = logging.getLogger(self.app_name)
      log.info("Downloading music: " + item.url + " " + item.title)
      # TODO pass dir?

      file_name = Path(item.artist) / item.album / item.title
      file_name = str(file_name) + ".mp3"
      file_name = fix_path_for_windows(file_name)

      yt = ytdlp.YTDLP(item.url)
      yt.download_audio(file_name)

   def t_download_video(self, item):
      log = logging.getLogger(self.app_name)

      log.info("Downloading video: " + item.url + " " + item.title)

      yt = ytdlp.YTDLP(item.url)
      yt.download_video('file.mp4')

   def t_download_link_details(self, item):
      log = logging.getLogger(self.app_name)
      #log.info("Downloading details: " + item.url + " " + item.title)

      from .files.returnyoutubedislikeapijson import YouTubeThumbsDown
      code = item.get_video_code()

      y = YouTubeLinkComposite(item.url)
      y.download_details()

   def t_download_channel_details(self, item):
      log = logging.getLogger(self.app_name)
      log.info("Downloading channel details: ")

   def t_refresh(self, item):
      log = logging.getLogger(self.app_name)
      log.info("Refreshing")

      from .models import VideoLinkDataModel
      objs = VideoLinkDataModel.objects.all()
      for obj in objs:
          self.download_link_details(obj)

   def download_music(self, item):
       self.threads[0].add_to_process_list(item)

   def download_video(self, item):
       self.threads[1].add_to_process_list(item)

   def download_link_details(self, item):
       self.threads[2].add_to_process_list(item)

   def download_channel_details(self, item):
       self.threads[3].add_to_process_list(item)

   def get_export_path(self):
       return self.directory / 'exports' / self.app_name

   def get_data_path(self):
       return self.directory / 'data' / self.app_name
