from notifications.urls import urlpatterns
from applications.notifications_extension.views import mark_as_read_and_redirect
from django.urls import include, re_path as url, path
from . import views

# from .api import urls

app_name = 'notifications'

urlpatterns = [
        url(r'^mark-as-read-and-redirect/(?P<slug>\d+)/$', views.mark_as_read_and_redirect, name='mark_as_read_and_redirect'),
        url(r'^delete/(?P<slug>\d+)/$', views.delete, name='delete'),
        url(r'^api/',include('applications.notifications_extension.api.urls')),
    ] + urlpatterns
