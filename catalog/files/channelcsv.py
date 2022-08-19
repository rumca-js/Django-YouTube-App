
class ChannelData(object):
    def __init__(self, row_data):
         delimiter = ";"
         channel_info = row_data.split(delimiter)

         self.url = channel_info[0]
         self.artist = channel_info[1]
         self.title = channel_info[1]

         self.album = ""
         self.dead = False
         self.category = ""
         self.subcategory = ""

    def to_string(channel):
        return "{0};{1}".format(channel.url, channel.title)


class ChannelsData(object):
    def __init__(self, data):
        delimiter = "\n"
        channels = data.split(delimiter)
        self.channels = []

        for channel_row in channels:
             channel_row = channel_row.replace("\r", "")
             channel = ChannelData(channel_row)
             self.channels.append(channel)


