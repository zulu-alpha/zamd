"""Common helper funcions"""
import json
import requests


CACHE: dict = dict()


def get_requests_object(url: str) -> requests.models.Response:
    """Memoization for web requests"""
    if url not in CACHE:
        request = requests.get(url)
        assert request.status_code == 200
        CACHE[url] = request
    return CACHE[url]


def make_filename_safe(filename: str) -> str:
    """Return a unix safe version of the given filename"""
    safe_characters = (" ", ".", "_", "@")
    filename = "".join(
        c for c in filename if c.isalnum() or c in safe_characters
    ).rstrip()
    filename = filename.replace(" ", "_")
    return filename.lower()


def get_mods_manifest(manifest_url: str) -> dict:
    """Get a dictionary of the manifest at the given URL"""
    return json.loads(get_requests_object(manifest_url).text)
