from datetime import date
from datetime import datetime
import json

from django.db import models

from statusite.youtube.utils import youtube_api_wrapper


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {} not serializable".format(type(obj)))


class Playlist(models.Model):
    youtube_id = models.CharField(max_length=255)
    json_str = models.TextField(blank=True, editable=False, null=True)
    title = models.CharField(blank=True, editable=False, max_length=255, null=True)

    def __str__(self):
        return self.title if self.title else self.youtube_id

    def reload(self):
        youtube_api = youtube_api_wrapper()
        results_playlists = (
            youtube_api.playlists().list(id=self.youtube_id, part="snippet").execute()
        )
        self.title = results_playlists["items"][0]["snippet"]["title"]
        results_playlistItems = (
            youtube_api.playlistItems()
            .list(
                maxResults=3, part="snippet,contentDetails", playlistId=self.youtube_id
            )
            .execute()
        )

        # Make sure maxres thumbail is present for each item,
        # by copying the default thumbnail if necessary.
        for item in results_playlistItems["items"]:
            thumbnails = item["snippet"]["thumbnails"]
            if "maxres" not in thumbnails and "default" in thumbnails:
                thumbnails["maxres"] = thumbnails["default"]

        self.json_str = json.dumps(results_playlistItems, default=json_serial)
        self.save()
