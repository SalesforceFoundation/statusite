
import json 
from datetime import datetime    

from django.test import TestCase
# Not sure why these need to be imported this way.
from statusite.repository.models import Release, Repository
from build_events.models import BuildResult


class TestBuildReleaseWebhook(TestCase):
    def setUp(self):
        self.repo = Repository(
            owner='Test',
            name='TestRepo', 
            product_name='Test', 
            github_id=1, 
            url='https://example.com/Test/TestRepo'
        )
        self.repo.save()
        self.release = Release(
            repo = self.repo,
            name = 'Version 1',
            version ='Version 1',
            beta = True,
            release_notes = 'Sample Release Notes',
            url = 'https://example.com/Test/TestRepo/releases/tag/uat%2FVersion%201',
            github_id = 100,
            time_created = datetime.now(),
            tag = 'uat/Version 1' 
        )
        self.release.save()

    def test_build_release_webhook(self):
        build_event = {
            'repository': {
                'name': 'TestRepo',
                'owner': 'Test'
            },
            'build': {
                'tag': 'uat/Version 1',
                'plan': 'Upload Beta',
                'id': 3000,
                'status': 'SUCCESS',
                'start_date': datetime.today().date().isoformat(),
                'tests_pass': 10,
                'tests_fail': 0,
                'tests_total': 10
            }
        }
        response = self.client.post('/webhook/mbci/build', json.dumps(build_event), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        build = BuildResult.objects.get(repo = self.repo)
        self.assertEqual(build.mbci_build_id, 3000)
