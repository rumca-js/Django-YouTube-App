

class LinkData(object):
    def __init__(self, row_data):
         delimiter = ";"
         link_info = row_data.split(delimiter)

         self.url = link_info[0]
         self.artist = link_info[1]
         self.album = link_info[2]
         self.title = link_info[3]
         self.dead = link_info[4]
         self.category = link_info[5]
         self.subcategory = link_info[6]

    def to_string(link):
        return "{0};{1};{2};{3};{4};{5}".format(link.url, link.artist, link.album, link.title, "False", link.category, link.subcategory)


class LinksData(object):
    def __init__(self, data):
        delimiter = "\n"
        links = data.split(delimiter)
        self.links = []

        for link_row in links:
             link_row = link_row.replace("\r", "")
             link = LinkData(link_row)
             self.links.append(link)


