#!/usr/bin/env python3
import os
from urllib.parse import quote
import requests
import config


def api(method: str, endpoint: str, json: dict = None) -> requests.Response:
    url = config.URL.rstrip("/") + endpoint
    auth_data = {"x-api-key": config.KEY}

    response = requests.api.request(method, url, headers=auth_data, json=json)
    return response


def main():
    event_type = os.environ.get("sonarr_eventtype") or os.environ.get("radarr_eventtype")

    if event_type in ["SeriesDelete", "MovieDelete"]:
        deleted_files = os.environ.get("sonarr_series_deletedfiles") or os.environ.get("radarr_movie_deletedfiles")

        if deleted_files == "True":
            title = os.environ.get("sonarr_series_title") or os.environ.get("radarr_movie_title")
            imdb_id = os.environ.get("sonarr_series_imdbid") or os.environ.get("radarr_movie_imdbid")
            tvdb_id = os.environ.get("sonarr_series_tvdbid")
            tmdb_id = os.environ.get("radarr_movie_tmdbid")

            search = api("GET", f"/search?query={quote(title)}").json()
            search = [x["mediaInfo"] for x in search["results"] if "mediaInfo" in x]

            for item in search:
                if item is not None:
                    env_ids = list(filter(None, [tvdb_id, tmdb_id, imdb_id]))
                    seerr_ids = list(filter(None, [str(item["tvdbId"]), str(item["tmdbId"]), item["imdbId"]]))

                    if any((x in seerr_ids) for x in env_ids):
                        if config.CLEAR_DATA:
                            api("DELETE", f"/media/{item['id']}")
                        else:
                            issue_data = {"issueType": 4, "message": "Removed from library", "mediaId": item["id"]}
                            api("POST", "/issue", json=issue_data)


if __name__ == "__main__":
    main()
