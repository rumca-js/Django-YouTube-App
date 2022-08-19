from django.shortcuts import render
from django.views import generic

from django.db.models.query import QuerySet
from django.db.models.query import EmptyQuerySet

from .models import VideoLinkDataModel, VideoChannelDataModel, YouTubeLinkBasic
from .forms import NewLinkForm, ImportLinksForm, ChoiceForm, NewChannelForm, ImportChannelsForm
from .files.linkcsv import LinksData, LinkData
from .files.channelcsv import ChannelsData, ChannelData


def index(request):
    c = Configuration.get_object()

    # Generate counts of some of the main objects
    num_links = VideoLinkDataModel.objects.all().count()
    num_channels = VideoChannelDataModel.objects.all().count()

    context = {
        'num_links': num_links,
        'num_channels': num_channels,
        'page_title': "YouTube Index",
    }
    context['version'] = c.version

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class LinkListView(generic.ListView):
    model = VideoLinkDataModel
    context_object_name = 'link_list'
    #paginate_by = 10

    def get_queryset(self):
        parameter_map = self.get_filters()
        self._tmp = VideoLinkDataModel.objects.filter(**parameter_map)

        return self._tmp

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LinkListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context

        categories = self.get_uniq('category')
        subcategories = self.get_uniq('subcategory')
        artists = self.get_uniq('artist')
        albums = self.get_uniq('album')

        categories = self.to_dict(categories)
        subcategories = self.to_dict(subcategories)
        artists = self.to_dict(artists)
        albums = self.to_dict(albums)

        category_form = ChoiceForm(categories = categories,
                                    subcategories = subcategories,
                                    artists = artists,
                                    albums = albums,
                                    filters = self.get_filters())

        context['category_form'] = category_form
        context['page_title'] = "YouTubeIndex Link List"

        return context

    def get_uniq(self, field):
        values = set()
        for val in self._tmp.values(field):
            if str(val).strip() != "":
                values.add(val[field])
        return values

    def to_dict(self, alist):
        result = [('Any', 'Any')]
        for item in sorted(alist):
            if item.strip() != "":
                result.append((item, item))
        return result

    def get_filters(self):
        parameter_map = {}

        category = self.request.GET.get("category")
        if category and category != "Any":
           parameter_map['category'] = category

        subcategory = self.request.GET.get("subcategory")
        if subcategory and subcategory != "Any":
           parameter_map['subcategory'] = subcategory

        artist = self.request.GET.get("artist")
        if artist and artist != "Any":
           parameter_map['artist'] = artist

        album = self.request.GET.get("album")
        if album and album != "Any":
           parameter_map['album'] = album
        return parameter_map


class LinkDetailView(generic.DetailView):
    model = VideoLinkDataModel

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LinkDetailView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        #url = self.object.url

        #if VideoLinkDataModel.objects.filter(url=url).exists():
        #    # TODO test if it is youtube
        #    obj = YouTubeLinkBasic(self.object.url)
        #    context['embed_link'] = obj.get_embed_link()
        context['page_title'] = self.object.title
        return context


def add_link(request):
    method = "x"
    additional_text = "y"
    context = {}

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = "POST"

        # create a form instance and populate it with data from the request:
        form = NewLinkForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            url = form.cleaned_data['url']
            artist = form.cleaned_data['artist']
            album = form.cleaned_data['album']
            category = form.cleaned_data['category']
            subcategory = form.cleaned_data['subcategory']
            title = form.cleaned_data['title']

            ft = VideoLinkDataModel.objects.filter(url=url)
            if ft.exists():
                context['form'] = form
                context['link'] = ft[0]
                context['page_title'] = "Add link"
                return render(request, 'add_link_exists.html', context)
            else:
                record = VideoLinkDataModel(url=url,
                                            artist=artist,
                                            album=album,
                                            title=title,
                                            category=category,
                                            subcategory=subcategory)
                record.save()

                context = {'form': form, 'method': method}
                context['page_title'] = "Add link"
                context['link'] = record
                return render(request, 'add_link_added.html', context)
        #    # process the data in form.cleaned_data as required
        #    # ...
        #    # redirect to a new URL:
        #    #return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewLinkForm()

    context = {'form': form,}
    context['page_title'] = "Add link"
    return render(request, 'add_link.html', context)


def import_links(request):
    method = "x"
    summary_text = ""
    context = {}

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = "POST"

        # create a form instance and populate it with data from the request:
        form = ImportLinksForm(request.POST)

        if form.is_valid():
            rawlinks = form.cleaned_data['rawlinks']
            links = LinksData(rawlinks)
            for link in links.links:

                if VideoLinkDataModel.objects.filter(url=link.url).exists():
                    summary_text += link.title + " " + link.url + " " + link.artist + " Error: Already present in db\n"
                else:
                    record = VideoLinkDataModel(url=link.url,
                                                artist=link.artist,
                                                album=link.album,
                                                title=link.title,
                                                category=link.category,
                                                subcategory=link.subcategory)
                    record.save()
                    summary_text += link.title + " " + link.url + " " + link.artist + " OK\n"

        context["form"] = form
        context['summary_text'] = summary_text
        return render(request, 'import_links_summary.html', context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ImportLinksForm()
        context["form"] = form
        context['page_title'] = "Import links"
        return render(request, 'import_links.html', context)


def remove_link(request, pk):
    context = []
    context['page_title'] = "Remove link"

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if ft.exists():
        ft.delete()
        return render(request, 'remove_link_ok.html', context)
    else:
        return render(request, 'remove_link_nok.html', context)


def remove_all_links(request):
    context = []
    context['page_title'] = "Remove all links"

    ft = VideoLinkDataModel.objects.all()
    if ft.exists():
        ft.delete()
        return render(request, 'remove_all_links_ok.html', context)
    else:
        return render(request, 'remove_all_links_nok.html', context)


class ChannelListView(generic.ListView):
    model = VideoChannelDataModel
    context_object_name = 'channel_list'
    #paginate_by = 10

    def get_queryset(self):
        self._tmp = VideoChannelDataModel.objects.all()

        return self._tmp

    def get_context_data(self, **kwargs):
        context = super(ChannelListView, self).get_context_data(**kwargs)
        context['page_title'] = "YouTubeIndex"
        return context


class ChannelDetailView(generic.DetailView):
    model = VideoChannelDataModel

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ChannelDetailView, self).get_context_data(**kwargs)

        context['page_title'] = self.object.title
        return context

def add_channel(request):
    context = {}
    form = None

    if request.method == 'POST':
        form = NewChannelForm(request.POST)
    else:
        form = NewChannelForm()

    context["form"] = form
    context['page_title'] = "Add channel"
    return render(request, 'add_channel.html', context)


def import_channels(request):
    context = {}
    form = None
    summary_text = ""

    if request.method == 'POST':
        form = ImportChannelsForm(request.POST)

        if form.is_valid():

            rawchannels = form.cleaned_data['rawchannels']
            channels = ChannelsData(rawchannels)
            for channel in channels.channels:

                if VideoChannelDataModel.objects.filter(url=channel.url).exists():
                    summary_text += channel.title + " " + channel.url + " " + channel.artist + " Error: Already present in db\n"
                else:
                    record = VideoChannelDataModel(url=channel.url,
                                                artist=channel.artist,
                                                album=channel.album,
                                                title=channel.title,
                                                category=channel.category,
                                                subcategory=channel.subcategory)
                    record.save()
                    summary_text += channel.title + " " + channel.url + " " + channel.artist + " OK\n"
        return render(request, 'import_channels_summary.html', context)
    else:
        form = ImportChannelsForm()

        context["form"] = form
        context["summary_text"] = summary_text
        context['page_title'] = "Import channels"
        return render(request, 'import_channels.html', context)


def remove_channel(request, pk):
    context = {}
    context['page_title'] = "Remove channel"

    ft = VideoChannelDataModel.objects.filter(id=pk)
    if ft.exists():
        ft.delete()
        return render(request, 'remove_channel_ok.html', context)
    else:
        return render(request, 'remove_channel_nok.html', context)


def remove_all_channels(request):
    context = {}
    context['page_title'] = "Remove channel"

    ft = VideoChannelDataModel.objects.all()
    if ft.exists():
        ft.delete()
        return render(request, 'remove_all_channels_ok.html', context)
    else:
        return render(request, 'remove_all_channels_nok.html', context)


def export_data(request):
    ft = VideoChannelDataModel.objects.all()
    summary_text = ""

    links = VideoLinkDataModel.objects.all()
    for link in links:
        data = LinkData.to_string(link)
        summary_text += data + "\n"

    channels = VideoChannelDataModel.objects.all()
    for channel in channels:
        data = ChannelData.to_string(channel)
        summary_text += data + "\n"

    context = {"summary_text": summary_text}
    context['page_title'] = "Export data"

    return render(request, 'summary_present.html', context)


from .prjconfig import Configuration

def configuration(request):
    context = {}
    context['page_title'] = "Configuration"
    c = Configuration.get_object()
    context['directory'] = c.directory
    context['version'] = c.version

    threads = c.get_threads()
    for thread in threads:
        items = thread.get_processs_list()

    context['thread_list'] = threads

    return render(request, 'configuration.html', context)


def download_music(request, pk):
    context = {}
    context['page_title'] = "Download Music"

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if ft.exists():
        context["summary_text"] = "Added to download queue"
    else:
        context["summary_text"] = "Failed to add to download queue"

    c = Configuration.get_object()
    c.download_music(ft[0])

    return render(request, 'summary_present.html', context)


def download_video(request, pk):
    context = {}
    context['page_title'] = "Download Video"

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if ft.exists():
        context["summary_text"] = "Added to download queue"
    else:
        context["summary_text"] = "Failed to add to download queue"

    c = Configuration.get_object()
    c.download_video(ft[0])

    return render(request, 'summary_present.html', context)


def edit_video(request, pk):
    context = {}
    context['page_title'] = "Edit Video"

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if ft.exists():
        context["summary_text"] = "x"
    else:
        context["summary_text"] = "x"

    return render(request, 'summary_present.html', context)
