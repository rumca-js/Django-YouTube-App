"""
These types represent commonly used elements: link, channel.
"""

import os
import time
import logging
import shutil
import urllib.request, urllib.error, urllib.parse


def get_page(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webContent = urllib.request.urlopen(req).read().decode('UTF-8')
        return webContent
    except Exception as e:
       logging.critical(e, exc_info=True)


def get_ascii_text(text):
  thebytes = text.encode('ascii', 'ignore')
  return thebytes.decode()


def fix_path_for_windows(file_path):
    chars = [
            #"/",
            ">",
            "<",
            ":",
            #"\\",
            "|",
            "?",
            "*",
            '"',
            "'",
            ]

    for item in chars:
        file_path = file_path.replace(item, "")

    file_path = " ".join(file_path.split())
    file_path = file_path.strip()

    return file_path
