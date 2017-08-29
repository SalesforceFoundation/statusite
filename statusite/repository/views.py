import hmac
import json
import re

import dateutil.parser
from hashlib import sha1
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from statusite.repository.models import Release
from statusite.repository.models import Repository
from statusite.repository.serializers import ReleaseSerializer
from statusite.repository.serializers import RepositorySerializer
from statusite.repository.utils import parse_times

def repo_list(request, owner=None):
    repos = Repository.objects.all()

    context = {
        'repos': repos,
    }
    return render(request, 'repository/repo_list.html', context=context)

def repo_detail(request, owner, name):
    query = {
        'owner': owner,
        'name': name,
    }
    repo = get_object_or_404(Repository, **query)

    context = {
        'repo': repo,
        'releases': repo.releases.all().order_by('time_created')
    }
    return render(request, 'repository/repo_detail.html', context=context)


class ReleaseDetailView(DetailView):
    model = Release
    context_object_name = 'release'

def validate_github_webhook(request):
    key = settings.GITHUB_WEBHOOK_SECRET
    signature = request.META.get('HTTP_X_HUB_SIGNATURE').split('=')[1]
    mac = hmac.new(bytearray(key, 'utf8'), msg=request.body, digestmod=sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return False
    return True

@csrf_exempt
@require_POST
def github_release_webhook(request):
    if not validate_github_webhook(request):
        return HttpResponseForbidden

    release_event = json.loads(request.body.decode('utf-8')) 

    repo_id = release_event['repository']['id']
    try:
        repo = Repository.objects.get(github_id = repo_id)
    except Repository.DoesNotExist:
        return HttpResponse('Not listening for this repository')

    time_created = dateutil.parser.parse(release_event['release']['created_at'])

    release_notes = release_event['release']['body']
    if not release_notes:
        release_notes = ''
  
    time_sandbox, time_prod = parse_times(release_notes)
    release = Release(
        repo = repo,
        name = release_event['release']['name'],
        version = release_event['release']['name'],
        beta = release_event['release']['prerelease'],
        release_notes = release_notes,
        url = release_event['release']['html_url'],
        github_id = release_event['release']['id'],
        time_created = time_created,
        time_push_sandbox = time_sandbox,
        time_push_prod = time_prod,
        tag = release_event['release']['tag_name']
    ) 
    release.save()

    return HttpResponse('OK')


class ApiRepository(RetrieveAPIView):
    """
    API endpoint that allows repositories to be viewed.
    """
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all().order_by('owner','name')

    @method_decorator(cache_page(60))
    def dispatch(self, *args, **kwargs):
        return super(ApiRepository, self).dispatch(*args, **kwargs)

    def get(self, request, owner, repo):
        repo = self.queryset.get(owner=owner, name=repo)
        serializer = self.serializer_class(repo)
        return Response(serializer.data)


class ApiRelease(RetrieveAPIView):
    """
    API endpoint to view a single release
    """
    serializer_class = ReleaseSerializer
    queryset = Repository.objects.all()

    @method_decorator(cache_page(60))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, owner, repo, version):
        repo = self.queryset.get(owner=owner, name=repo)
        release = repo.releases.get(version=version)
        serializer = self.serializer_class(release)
        return Response(serializer.data)
