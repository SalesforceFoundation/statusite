from datetime import datetime, timedelta
from hashlib import sha1
import hmac
import json

from django.conf import settings
import pytest
import pytz


@pytest.mark.django_db
class TestGithubWebhook:
    def _sign_request(self, body):
        return hmac.new(
            bytearray(settings.GITHUB_WEBHOOK_SECRET, "utf8"),
            msg=body.encode("utf-8"),
            digestmod=sha1,
        ).hexdigest()

    def test_post(self, client, repository_factory):
        repo = repository_factory()

        body = json.dumps(
            {
                "repository": {"id": 1},
                "release": {
                    "body": "Sandbox orgs: 2019-06-11\nProduction orgs: 2019-06-18",
                    "name": "1.0",
                    "prerelease": False,
                    "html_url": "",
                    "id": 1,
                    "created_at": "2019-06-17T16:47:22Z",
                },
            }
        )
        signature = self._sign_request(body)

        response = client.post(
            "/repo/webhook/github/release",
            data=body,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE=f"sha1={signature}",
        )

        assert response.status_code == 200
        assert response.content == b"OK"
        release = repo.releases.get()
        assert release.time_push_sandbox == datetime(2019, 6, 11, tzinfo=pytz.UTC)
        assert release.time_push_prod == datetime(2019, 6, 18, tzinfo=pytz.UTC)

    def test_invalid_signature(self, client):
        response = client.post(
            "/repo/webhook/github/release", HTTP_X_HUB_SIGNATURE=f"sha1=BOGUS"
        )
        assert response.status_code == 403

    def test_repository_not_found(self, client):
        body = json.dumps({"repository": {"id": 1}})
        signature = self._sign_request(body)

        response = client.post(
            "/repo/webhook/github/release",
            data=body,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE=f"sha1={signature}",
        )

        assert response.status_code == 200
        assert response.content == b"Not listening for this repository"


@pytest.mark.django_db
class TestApiRepository:
    def test_get(self, client, repository_factory, release_factory):
        repo = repository_factory()
        in_the_past = datetime(2019, 6, 16, 0, 0, 0, tzinfo=pytz.UTC)
        final_release = release_factory(
            repo=repo, time_push_prod=in_the_past, time_push_sandbox=in_the_past
        )
        beta_release = release_factory(
            name="1.0 (Beta 1)", version="1.0 (Beta 1)", repo=repo, beta=True
        )

        response = client.get("/api/repository/TestOwner/TestRepo")

        assert response.status_code == 200
        assert response.json() == {
            "github_id": 1,
            "latest_beta": {
                "beta": True,
                "name": "1.0 (Beta 1)",
                "release_notes": "",
                "release_notes_html": "",
                "time_created": "2019-06-17T00:00:00Z",
                "time_push_prod": None,
                "time_push_sandbox": None,
                "url": "",
                "version": "1.0 (Beta 1)",
            },
            "latest_release": {
                "beta": False,
                "name": "1.0",
                "release_notes": "",
                "release_notes_html": "",
                "time_created": "2019-06-17T00:00:00Z",
                "time_push_prod": "2019-06-16T00:00:00Z",
                "time_push_sandbox": "2019-06-16T00:00:00Z",
                "url": "",
                "version": "1.0",
            },
            "name": "TestRepo",
            "owner": "TestOwner",
            "product_name": "Test",
            "production_release": {
                "beta": False,
                "name": "1.0",
                "release_notes": "",
                "release_notes_html": "",
                "time_created": "2019-06-17T00:00:00Z",
                "time_push_prod": "2019-06-16T00:00:00Z",
                "time_push_sandbox": "2019-06-16T00:00:00Z",
                "url": "",
                "version": "1.0",
            },
            "sandbox_release": {
                "beta": False,
                "name": "1.0",
                "release_notes": "",
                "release_notes_html": "",
                "time_created": "2019-06-17T00:00:00Z",
                "time_push_prod": "2019-06-16T00:00:00Z",
                "time_push_sandbox": "2019-06-16T00:00:00Z",
                "url": "",
                "version": "1.0",
            },
            "url": "https://github.com/TestOwner/TestRepo",
        }


@pytest.mark.django_db
class TestApiRelease:
    def test_get(self, client, release_factory):
        release = release_factory()

        response = client.get("/api/repository/TestOwner/TestRepo/1.0")

        assert response.status_code == 200
        result = response.json()
        del result["time_created"]
        assert result == {
            "beta": False,
            "name": "1.0",
            "release_notes": "",
            "release_notes_html": "",
            "time_push_prod": None,
            "time_push_sandbox": None,
            "url": "",
            "version": "1.0",
        }
