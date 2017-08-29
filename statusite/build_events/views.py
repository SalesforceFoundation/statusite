import json
import hmac
from hashlib import sha1

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from statusite.repository.models import Release
from statusite.repository.models import Repository
from build_events.models import BuildResult

@csrf_exempt
@require_POST
def mrbelvedereci_build_webhook(request):
    #TODO: are these response values okay?
    #TODO: class based?


    if not validate_mrbelvedereci_webhook(request):
        raise PermissionDenied

    build_event = json.loads(request.body.decode('utf-8')) 
    owner = build_event['repository']['owner']
    repo_name = build_event['repository']['name']
    try:
        repo = Repository.objects.get(owner = owner, name = repo_name)
    except Repository.DoesNotExist:
        return HttpResponse('Not listening for this repository')

    # find the appropriate release for this build
    try:
        release = Release.objects.get(repo = repo, tag = build_event['build']['tag'])
    except Release.DoesNotExist:
        return HttpResponse('Invalid release')

    build_result = BuildResult(
        repo = repo,
        release = release,
        plan_name = build_event['build']['plan'],
        mbci_build_id = build_event['build']['id'],
        status = build_event['build']['status'],
        build_date = build_event['build']['start_date'],
        tests_passed = build_event['build']['tests_pass'],
        tests_failed = build_event['build']['tests_fail'],
        tests_total = build_event['build']['tests_total'],
    )
    build_result.save()
    return HttpResponse('OK')


def validate_mrbelvedereci_webhook(request):
    if not settings.STATUSITE_WEBHOOK_VERIFY:
        return True

    key = settings.STATUSITE_WEBHOOK_SECRET
    signature = request.META.get('HTTP_X_MBCI_SIGNATURE').split('=')[1]
    mac = hmac.new(bytearray(key, 'utf8'), msg=request.body, digestmod=sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return False
    return True
