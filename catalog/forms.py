from django import forms
from .models import VideoLinkDataModel, VideoChannelDataModel

# https://docs.djangoproject.com/en/4.1/ref/forms/widgets/


class NewLinkForm(forms.ModelForm):
    """
    New link form
    """
    class Meta:
        model = VideoLinkDataModel
        fields = ['url', 'artist', 'album', 'title', 'category', 'subcategory']


class NewChannelForm(forms.ModelForm):
    """
    New channel form
    """
    class Meta:
        model = VideoChannelDataModel
        fields = ['url', 'artist', 'album', 'title', 'category', 'subcategory']


class ImportLinksForm(forms.Form):
    """
    Import links form
    """
    rawlinks = forms.CharField(widget=forms.Textarea(attrs={'name':'rawlinks', 'rows':30, 'cols':100}))


class ImportChannelsForm(forms.Form):
    """
    Import channels form
    """
    rawchannels = forms.CharField(widget=forms.Textarea(attrs={'name':'rawchannels', 'rows':30, 'cols':100}))


class LinkSelectionForm(forms.Form):
    """
    Category choice form
    """

    category = forms.CharField(widget=forms.Select(choices=()))
    subcategory = forms.CharField(widget=forms.Select(choices=()))
    artist = forms.CharField(widget=forms.Select(choices=()))
    album = forms.CharField(widget=forms.Select(choices=()))
    search = forms.CharField(label='Search', max_length = 500, required=False)

    def __init__(self, *args, **kwargs):
        self.args = kwargs.pop('args', ())
        super().__init__(*args, **kwargs)

    def get_filtered_objects(self):
        parameter_map = self.get_filter_args()

        if 'search' in parameter_map:
            print("parameters: " + parameter_map['search'])
            parameter_map["title__icontains"] = parameter_map['search']
            del parameter_map['search']

        self.filtered_objects = VideoLinkDataModel.objects.filter(**parameter_map)
        return self.filtered_objects

    def create(self):
        # how to unpack dynamic forms
        # https://stackoverflow.com/questions/60393884/how-to-pass-choices-dynamically-into-a-django-form
        categories = self.get_filtered_objects_values('category')
        subcategories = self.get_filtered_objects_values('subcategory')
        artists = self.get_filtered_objects_values('artist')
        albums = self.get_filtered_objects_values('album')

        # custom javascript code
        # https://stackoverflow.com/questions/10099710/how-to-manually-create-a-select-field-from-a-modelform-in-django
        attr = {"onchange" : "this.form.submit()"}

        # default form value
        # https://stackoverflow.com/questions/604266/django-set-default-form-values
        category_init = self.get_init('category')
        subcategory_init = self.get_init('subcategory')
        artist_init = self.get_init('artist')
        album_init = self.get_init('album')

        self.fields['category'] = forms.CharField(widget=forms.Select(choices=categories, attrs=attr), initial=category_init)
        self.fields['subcategory'] = forms.CharField(widget=forms.Select(choices=subcategories, attrs=attr), initial=subcategory_init)
        self.fields['artist'] = forms.CharField(widget=forms.Select(choices=artists, attrs=attr), initial=artist_init)
        self.fields['album'] = forms.CharField(widget=forms.Select(choices=albums, attrs=attr), initial=album_init)
        self.fields['search'] = forms.CharField(label='Search', max_length = 500, required=False, initial=self.args.get("search"))

    def get_init(self, column):
        filters = self.get_filter_args()
        if column in filters:
            return filters[column]
        else:
            return "Any"

    def get_filtered_objects_values(self, field):
        values = set()
        values.add("Any")

        for val in self.filtered_objects.values(field):
            if str(val).strip() != "":
                values.add(val[field])

        dict_values = self.to_dict(values)

        return dict_values

    def to_dict(self, alist):
        result = []
        for item in sorted(alist):
            if item.strip() != "":
                result.append((item, item))
        return result

    def get_filter_args(self):
        parameter_map = {}

        category = self.args.get("category")
        if category and category != "Any":
           parameter_map['category'] = category

        subcategory = self.args.get("subcategory")
        if subcategory and subcategory != "Any":
           parameter_map['subcategory'] = subcategory

        artist = self.args.get("artist")
        if artist and artist != "Any":
           parameter_map['artist'] = artist

        album = self.args.get("album")
        if album and album != "Any":
           parameter_map['album'] = album

        search = self.args.get("search")
        if search:
           parameter_map['search'] = search

        return parameter_map

    def get_filter_string(self):
        filters = self.get_filter_args()
        filter_string = ""
        for key in filters:
            filter_string += "&{0}={1}".format(key, filters[key])

        return filter_string
