
class ChannelData(object):
    def __init__(self, row_data):
         delimiter = ";"
         channel_info = row_data.split(delimiter)

         self.url = channel_info[0]
         self.artist = channel_info[1]
         self.album = channel_info[2]
         self.title = channel_info[3]
         self.category = channel_info[4]
         self.subcategory = channel_info[5]

    def to_string(channel):
        return "{0};{1};{2};{3};{4};{5}".format(channel.url,
                channel.artist,
                channel.album,
                channel.title,
                channel.category,
                channel.subcategory)


class ChannelsData(object):
    def __init__(self, data):
        delimiter = "\n"
        channels = data.split(delimiter)
        self.channels = []

        for channel_row in channels:
             channel_row = channel_row.replace("\r", "")
             channel = ChannelData(channel_row)
             self.channels.append(channel)


