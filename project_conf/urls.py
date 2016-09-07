from django.conf.urls import url
from django.contrib import admin
import main.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', main.views.index),
    url(r'^ldrbrd/(?P<contest_id>[1-9]\d*)/$', main.views.ldrbrd),
]
