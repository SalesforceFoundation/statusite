from datetime import datetime
from unittest import mock
import json

import pytest

from statusite.youtube.models import Playlist, json_serial


class TestPlaylist:
    def test_str(self):
        playlist = Playlist(title="Test")
        assert str(playlist) == "Test"

    @pytest.mark.django_db
    def test_reload(self, playlist_factory, mocker):
        build_api = mocker.patch("statusite.youtube.utils.build")
        build_api.return_value = youtube_api = mock.Mock()
        youtube_api.playlists.return_value.list.return_value.execute.return_value = {
            "items": [{"snippet": {"title": "Playlist Title"}}]
        }
        youtube_api.playlistItems.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "snippet": {
                        "title": "Item 1",
                        "publishedAt": datetime(2019, 6, 17),
                        "thumbnails": {"default": {"url": "bogus"}},
                    }
                }
            ]
        }
        playlist = playlist_factory()
        playlist.reload()

        assert playlist.title == "Playlist Title"
        result = json.loads(playlist.json_str)
        assert "maxres" in result["items"][0]["snippet"]["thumbnails"]

    def test_json_serial_unknown_type(self):
        with pytest.raises(TypeError):
            json_serial(None)
