from django import forms

# https://docs.djangoproject.com/en/4.1/ref/forms/widgets/


class NewLinkForm(forms.Form):
    """
    New link form
    """
    url = forms.CharField(label='Url', max_length = 100)
    category = forms.CharField(label='Category', max_length = 100)
    subcategory = forms.CharField(label='Subcategory', max_length = 100)
    artist = forms.CharField(label='Artist', max_length = 100)
    album = forms.CharField(label='Album', max_length = 100)
    title = forms.CharField(label='Title', max_length = 100)


class NewChannelForm(forms.Form):
    """
    New channel form
    """
    url = forms.CharField(label='Url', max_length = 100)
    category = forms.CharField(label='Category', max_length = 100)
    subcategory = forms.CharField(label='Subcategory', max_length = 100)
    artist = forms.CharField(label='Artist', max_length = 100)
    album = forms.CharField(label='Album', max_length = 100)
    title = forms.CharField(label='Title', max_length = 100)


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


class ChoiceForm(forms.Form):
    """
    Category choice form
    """

    category = forms.CharField(widget=forms.Select(choices=()))
    subcategory = forms.CharField(widget=forms.Select(choices=()))
    artist = forms.CharField(widget=forms.Select(choices=()))
    album = forms.CharField(widget=forms.Select(choices=()))

    def __init__(self, *args, **kwargs):
        # how to unpack dynamic forms
        # https://stackoverflow.com/questions/60393884/how-to-pass-choices-dynamically-into-a-django-form
        categories = kwargs.pop('categories', ())
        subcategories = kwargs.pop('subcategories', ())
        artists = kwargs.pop('artists', ())
        albums = kwargs.pop('albums', ())
        filters = kwargs.pop('filters', ())

        # custom javascript code
        # https://stackoverflow.com/questions/10099710/how-to-manually-create-a-select-field-from-a-modelform-in-django
        attr = {"onchange" : "this.form.submit()"}

        # default form value
        # https://stackoverflow.com/questions/604266/django-set-default-form-values
        category_init = 'Any'
        if 'category' in filters:
            category_init = filters['category']
        subcategory_init = 'Any'
        if 'subcategory' in filters:
            subcategory_init = filters['subcategory']
        artist_init = 'Any'
        if 'artist' in filters:
            artist_init = filters['artist']
        album_init = 'Any'
        if 'album' in filters:
            album_init = filters['album']

        selected = 'Music'

        super().__init__(*args, **kwargs)

        self.fields['category'] = forms.CharField(widget=forms.Select(choices=categories, attrs=attr), initial=category_init)
        self.fields['subcategory'] = forms.CharField(widget=forms.Select(choices=subcategories, attrs=attr), initial=subcategory_init)
        self.fields['artist'] = forms.CharField(widget=forms.Select(choices=artists, attrs=attr), initial=artist_init)
        self.fields['album'] = forms.CharField(widget=forms.Select(choices=albums, attrs=attr), initial=album_init)
