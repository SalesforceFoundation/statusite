from django.conf.urls import url

from statusite.repository import views as repository_views
from statusite.youtube import views as youtube_views
from rest_framework.schemas import get_schema_view


app_name = "api"
urlpatterns = [
    url(
        r"repository/(?P<owner>\w+)/(?P<repo>[^/].*)/(?P<version>.+)$",
        repository_views.ApiRelease.as_view(),
        name="api-release",
    ),
    url(
        r"repository/(?P<owner>\w+)/(?P<repo>[^/].*)$",
        repository_views.ApiRepository.as_view(),
        name="api-repository",
    ),
    url(
        r"youtube/playlists/(?P<youtube_id>.+)$",
        youtube_views.PlaylistView.as_view(),
        name="api-playlist",
    ),
]

schema_view = get_schema_view(title="Statusite API")
urlpatterns += (url(r"^schema/$", schema_view),)
