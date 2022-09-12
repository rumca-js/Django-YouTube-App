from django.shortcuts import render
from django.views import generic
from django.urls import reverse

from django.db.models.query import QuerySet
from django.db.models.query import EmptyQuerySet

from .models import VideoLinkDataModel, VideoChannelDataModel, YouTubeLinkComposite
from .forms import NewLinkForm, ImportLinksForm, ChoiceForm, NewChannelForm, ImportChannelsForm
from .files.linkcsv import LinksData, LinkData
from .files.channelcsv import ChannelsData, ChannelData
from .basictypes import *
from pathlib import Path


# https://stackoverflow.com/questions/66630043/django-is-loading-template-from-the-wrong-app
app_name = Path("catalog")


def init_context(context):
    context["page_title"] = "YouTube Index"
    context["django_app"] = str(app_name)
    context["base_generic"] = str(app_name / "base_generic.html")
    context["icon_size"] = "30px"

    c = Configuration.get_object()
    context['app_version'] = c.version

    return context

def get_context(request = None):
    context = {}
    context = init_context(context)
    return context


def index(request):
    # Generate counts of some of the main objects
    num_links = VideoLinkDataModel.objects.all().count()
    num_channels = VideoChannelDataModel.objects.all().count()

    context = get_context(request)

    context['num_links'] = num_links
    context['num_channels'] = num_channels

    # Render the HTML template index.html with the data in the context variable
    return render(request, app_name / 'index.html', context=context)


class LinkListView(generic.ListView):
    model = VideoLinkDataModel
    context_object_name = 'link_list'
    paginate_by = 20

    def get_queryset(self):
        self.filter_form = ChoiceForm(args = self.request.GET)
        return self.filter_form.get_filtered_objects()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LinkListView, self).get_context_data(**kwargs)
        context = init_context(context)
        # Create any data and add it to the context

        self.filter_form.create()
        self.filter_form.method = "GET"
        self.filter_form.action_url = reverse('catalog:links')

        context['category_form'] = self.filter_form
        context['page_title'] += " - Link List"

        from django_user_agents.utils import get_user_agent
        user_agent = get_user_agent(self.request)
        context["is_mobile"] = user_agent.is_mobile

        return context


class LinkDetailView(generic.DetailView):
    model = VideoLinkDataModel

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LinkDetailView, self).get_context_data(**kwargs)
        context = init_context(context)
        # Create any data and add it to the context
        #url = self.object.url

        context['page_title'] += " - " + self.object.title

        y = YouTubeLinkComposite(self.object.url)
        if not y.has_details():
            y.request_details_download()

        context['videodescription'] = y.get_description()
        context['videoviewcount'] = y.get_view_count()
        context['videothumbsup'] = y.get_thumbs_up()
        context['videothumbsdown'] = y.get_thumbs_down()
        context['videouploaddate'] = y.get_upload_date()
        context['videodead'] = y.get_dead()

        if self.request.GET.get("reset"):
            logging.info("Resetting")
            y.reset()

        return context


def add_link(request):
    context = get_context(request)
    context['page_title'] += " - Add link"

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = "POST"

        # create a form instance and populate it with data from the request:
        form = NewLinkForm(request.POST)

        ft = VideoLinkDataModel.objects.filter(url=request.POST.get('url'))
        if ft.exists():
            context['form'] = form
            context['link'] = ft[0]
            return render(request, app_name / 'add_link_exists.html', context)

        # check whether it's valid:
        if form.is_valid():
            form.save()

            context['form'] = form
            context['link'] = ft[0]
            return render(request, app_name / 'add_link_added.html', context)
        #    # process the data in form.cleaned_data as required
        #    # ...
        #    # redirect to a new URL:
        #    #return HttpResponseRedirect('/thanks/')
        else:
            context["summary_text"] = "Form is invalid"
            return render(request, app_name / 'summary_present.html', context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewLinkForm()
        form.method = "POST"
        form.action_url = reverse('catalog:addlink')
        context['form'] = form

    return render(request, app_name / 'form_basic.html', context)


def import_links(request):
    summary_text = ""
    context = get_context(request)
    context['page_title'] += " - Import links"

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
        return render(request, app_name / 'import_links_summary.html', context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ImportLinksForm()
        form.method = "POST"
        form.action_url = reverse('catalog:importlinks')
        context["form"] = form
        return render(request, app_name / 'form_basic.html', context)


def remove_link(request, pk):
    context = get_context(request)
    context['page_title'] += " - Remove link"

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if ft.exists():
        ft.delete()
        return render(request, app_name / 'remove_link_ok.html', context)
    else:
        return render(request, app_name / 'remove_link_nok.html', context)


def remove_all_links(request):
    context = get_context(request)
    context['page_title'] += "Remove all links"

    ft = VideoLinkDataModel.objects.all()
    if ft.exists():
        ft.delete()
        return render(request, app_name / 'remove_all_links_ok.html', context)
    else:
        return render(request, app_name / 'remove_all_links_nok.html', context)


class ChannelListView(generic.ListView):
    model = VideoChannelDataModel
    context_object_name = 'channel_list'
    paginate_by = 100

    def get_queryset(self):
        self._tmp = VideoChannelDataModel.objects.all()

        return self._tmp

    def get_context_data(self, **kwargs):
        context = super(ChannelListView, self).get_context_data(**kwargs)
        context = init_context(context)
        context['page_title'] += " - Channel list"
        return context


class ChannelDetailView(generic.DetailView):
    model = VideoChannelDataModel

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ChannelDetailView, self).get_context_data(**kwargs)
        context = init_context(context)

        context['page_title'] += self.object.title
        return context

def add_channel(request):
    context = get_context(request)
    context['page_title'] += " - Add channel"

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = "POST"

        # create a form instance and populate it with data from the request:
        form = NewChannelForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            form.save()

            ft = VideoChannelDataModel.objects.filter(url=model.url)
            if ft.exists():
                context['form'] = form
                context['channel'] = ft[0]
                return render(request, app_name / 'add_channel_exists.html', context)
            else:
                context['form'] = form
                context['channel'] = model
                return render(request, app_name / 'add_channel_added.html', context)
        else:
            context["summary_text"] = "Form is invalid"
            return render(request, app_name / 'summary_present.html', context)
        #    # process the data in form.cleaned_data as required
        #    # ...
        #    # redirect to a new URL:
        #    #return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewChannelForm()
        form.method = "POST"
        form.action_url = reverse('catalog:addchannel')
        context['form'] = form

    return render(request, app_name / 'form_basic.html', context)


def import_channels(request):
    context = get_context(request)
    context['page_title'] += " - Import channels"

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
        return render(request, app_name / 'import_channels_summary.html', context)
    else:
        form = ImportChannelsForm()
        form.method = "POST"
        form.action_url = reverse('catalog:importchannels')
        context["form"] = form

        context["summary_text"] = summary_text

        return render(request, app_name / 'form_basic.html', context)


def remove_channel(request, pk):
    context = get_context(request)
    context['page_title'] += " - Remove channel"

    ft = VideoChannelDataModel.objects.filter(id=pk)
    if ft.exists():
        ft.delete()
        return render(request, app_name / 'remove_channel_ok.html', context)
    else:
        return render(request, app_name / 'remove_channel_nok.html', context)


def remove_all_channels(request):
    context = get_context(request)
    context['page_title'] += "Remove all channels"

    ft = VideoChannelDataModel.objects.all()
    if ft.exists():
        ft.delete()
        return render(request, app_name / 'remove_all_channels_ok.html', context)
    else:
        return render(request, app_name / 'remove_all_channels_nok.html', context)


def export_data(request):
    context = get_context(request)
    context['page_title'] += " - Export data"

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
        
    context["summary_text"] = summary_text

    return render(request, app_name / 'summary_present.html', context)


from .prjconfig import Configuration

def configuration(request):
    context = get_context(request)
    context['page_title'] += " - Configuration"

    c = Configuration.get_object()
    context['directory'] = c.directory
    context['version'] = c.version
    context['database_size_bytes'] = get_directory_size_bytes(c.directory)
    context['database_size_kbytes'] = get_directory_size_bytes(c.directory)/1024
    context['database_size_mbytes'] = get_directory_size_bytes(c.directory)/1024/1024

    threads = c.get_threads()
    for thread in threads:
        items = thread.get_processs_list()

    context['thread_list'] = threads

    return render(request, app_name / 'configuration.html', context)


def download_music(request, pk):
    context = get_context(request)
    context['page_title'] += " - Download music"

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if ft.exists():
        context["summary_text"] = "Added to download queue"
    else:
        context["summary_text"] = "Failed to add to download queue"

    c = Configuration.get_object()
    c.download_music(ft[0])

    return render(request, app_name / 'summary_present.html', context)


def download_video(request, pk):
    context = get_context(request)
    context['page_title'] += " - Download video"

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if ft.exists():
        context["summary_text"] = "Added to download queue"
    else:
        context["summary_text"] = "Failed to add to download queue"

    c = Configuration.get_object()
    c.download_video(ft[0])

    return render(request, app_name / 'summary_present.html', context)


def edit_video(request, pk):
    context = get_context(request)
    context['page_title'] += " - Edit video"
    context['pk'] = pk

    ft = VideoLinkDataModel.objects.filter(id=pk)
    if not ft.exists():
       return render(request, app_name / 'edit_video_does_not_exist.html', context)

    obj = ft[0]

    if request.method == 'POST':
        form = NewLinkForm(request.POST, instance=obj[0])
        context['form'] = form

        if form.is_valid():
            form.save()

            ft = VideoLinkDataModel.objects.filter(url=model.url)
            if ft.exists():
                ft.delete()
                model.save()

                context['link'] = ft[0]
                return render(request, app_name / 'edit_video_ok.html', context)

        context['summary_text'] = "Could not edit video"

        return render(request, app_name / 'summary_present', context)
    else:
        form = NewLinkForm(instance=obj)
        form.method = "POST"
        form.action_url = reverse('catalog:editvideo', args = [pk])
        context['form'] = form
        return render(request, app_name / 'form_basic.html', context)


def edit_channel(request, pk):
    context = get_context(request)
    context['page_title'] += " - Edit channel"
    context['pk'] = pk

    ft = VideoChannelDataModel.objects.filter(id=pk)
    if not ft.exists():
       return render(request, app_name / 'edit_channel_does_not_exist.html', context)

    obj = ft[0]

    if request.method == 'POST':
        form = NewChannelForm(request.POST, instance=obj[0])
        context['form'] = form

        if form.is_valid():
            form.save()

            ft = VideoChannelDataModel.objects.filter(url=model.url)
            if ft.exists():
                ft.delete()

                context['link'] = ft[0]
                return render(request, app_name / 'edit_channel_ok.html', context)

        context['summary_text'] = "Could not edit video"

        return render(request, app_name / 'summary_present', context)
    else:
        form = NewChannelForm(instance=obj)
        form.method = "POST"
        form.action_url = reverse('catalog:editchannel', args = [pk])
        context['form'] = form
        return render(request, app_name / 'edit_channel.html', context)
