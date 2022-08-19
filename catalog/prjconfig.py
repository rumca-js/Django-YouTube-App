from pathlib import Path
from .threads import *
from .programwrappers import ytdlp
from .basictypes import *

class Configuration(object):
   obj = None

   def __init__(self):
       self.directory = Path(".").resolve()
       self.links_directory = self.directory / "link_files"
       self.channels_directory = self.directory / "channel_files"
       self.version = "0.0.1"
       self.server_log_file = self.directory / "server_log_file.txt"

       self.enable_logging()
       self.create_threads()

   def get_object():
       if not Configuration.obj:
           Configuration.obj = Configuration()
       return Configuration.obj

   def enable_logging(self):
       logging.shutdown()

       self.server_log_file.unlink(True)

       logging.basicConfig(level=logging.INFO, filename=self.server_log_file)

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
      logging.info("Downloading music: " + item.url + " " + item.title)
      # TODO pass dir?

      file_name = Path(item.artist) / item.album / item.title
      file_name = str(file_name) + ".mp3"
      file_name = fix_path_for_windows(file_name)

      yt = ytdlp.YTDLP(item.url)
      yt.download_audio(file_name)

   def t_download_video(self, item):
      logging.info("Downloading video: " + item.url + " " + item.title)

      yt = ytdlp.YTDLP(item.url)
      yt.download_video('file.mp4')

   def t_download_link_details(self, item):
      logging.info("Downloading link details: ")

      yt = ytdlp.YTDLP(item.url)
      yt.save_data('file.txt')

   def t_download_channel_details(self, item):
      logging.info("Downloading channel details: ")

   def t_refresh(self, item):
      logging.info("Refreshing: ")

   def download_music(self, item):
       self.threads[0].add_to_process_list(item)

   def download_video(self, item):
       self.threads[1].add_to_process_list(item)

   def download_link_details(self, item):
       self.threads[2].add_to_process_list(item)

   def download_channel_details(self, item):
       self.threads[3].add_to_process_list(item)