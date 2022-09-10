
from django.urls import path
from . import views

app_name = str(views.app_name)

urlpatterns = [
   path('', views.index, name='index'),
   path('links/', views.LinkListView.as_view(), name='links'),
   path('link/<int:pk>/', views.LinkDetailView.as_view(), name='link-detail'),
   path('addlink', views.add_link, name='addlink'),
   path('importlinks', views.import_links, name='importlinks'),
   path('removelink/<int:pk>/', views.remove_link, name='removelink'),
   path('removealllinks/', views.remove_all_links, name='removealllinks'),

   path('download_music/<int:pk>/', views.download_music, name='download_music'),
   path('download_video/<int:pk>/', views.download_video, name='download_video'),
   path('edit_video/<int:pk>/', views.edit_video, name='download_video'),

   path('channels/', views.ChannelListView.as_view(), name='channels'),
   path('channel/<int:pk>/', views.ChannelDetailView.as_view(), name='channel-detail'),
   path('addchannel', views.add_channel, name='addchannel'),
   path('importchannels', views.import_channels, name='importchannels'),
   path('removechannel/<int:pk>/', views.remove_channel, name='importchannels'),
   path('removeallchannels/', views.remove_all_channels, name='removeallchannels'),

   path('export/', views.export_data, name='exportdata'),
   path('configuration/', views.configuration, name='configuration'),
]
