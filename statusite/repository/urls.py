from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers
from statusite.repository import views as repository_views

router = routers.DefaultRouter()
#router.register(r'repos', repository_views.ApiRepository)

urlpatterns = [
    #url(r'^', include(router.urls)),
    url(r'webhook/github/release$', repository_views.github_release_webhook, name="github_release_webhook"),
    url(r'^release/(?P<pk>\d+)/$', repository_views.ReleaseDetailView.as_view(), name="release-detail"),
    url(r'^(?P<owner>\w+)/(?P<name>[^/].*)/*$', repository_views.repo_detail, name="repo_detail"),
]
