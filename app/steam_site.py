"""Code to scrape the Steam site for workshop item details"""
from typing import List, Set
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from bs4 import BeautifulSoup  # type: ignore
import click
from app import helpers


STEAM_WORKHOP_PAGE_URL = "https://steamcommunity.com/workshop/filedetails/"


def get_dependencies(url: str) -> List[str]:
    """Get steam workshop urls for all dependencies with the given mod's workshop url
    """
    soup = BeautifulSoup(helpers.get_requests_object(url).text, "html.parser")
    dependency_section = soup.find(id="RequiredItems")
    if dependency_section:
        return [link.get("href") for link in dependency_section.find_all("a")]
    return []


def get_id_from_url(url: str) -> str:
    """Get the id from the standard steam URL for a workshop item"""
    return parse_qs(urlparse(url).query)["id"][0]


def get_url_from_id(mod_id: str) -> str:
    """Get the workshop URL for the given mod's workshop ID"""
    scheme, netloc, path, params, query, fragment = urlparse(STEAM_WORKHOP_PAGE_URL)
    query = urlencode({"id": mod_id})
    return urlunparse((scheme, netloc, path, params, query, fragment))


def get_mod_title(url: str) -> str:
    """Get the title for the given steamworkshop URL"""
    soup = BeautifulSoup(helpers.get_requests_object(url).text, "html.parser")
    return soup.find_all("div", class_="workshopItemTitle")[0].contents[0]


def collect_all_dependencies(urls: Set[str]) -> Set[str]:
    """Return a set of all steamworkshop mods (dependencies and given urls) needed to
    use all the mods defined by the given urls
    """
    url_set = set(urls)
    traversed_mods: set = set()
    for url in urls:
        recurse_dependencies(url, url_set, traversed_mods)
    return url_set


def recurse_dependencies(first_url: str, url_set: set, traversed_mods: set) -> set:
    """Recurse dependencies for given url and add to given set"""
    for url in get_dependencies(first_url):
        if url not in traversed_mods:
            traversed_mods.add(url)
            url_set.add(url)
            recurse_dependencies(url, url_set, traversed_mods)
    return url_set


def get_updated_date(url: str) -> str:
    """Get the string as it appears on the steamworkshop page of when it was last
    updated
    """
    soup = BeautifulSoup(helpers.get_requests_object(url).text, "html.parser")
    details_column = soup.find_all("div", class_="detailsStatRight")
    try:
        date = details_column[2].contents[0]
    except IndexError:
        date = details_column[1].contents[0]
    return date


def get_all_mods_manifest_urls(manifest_dic: dict) -> Set[str]:
    """Return a set of urls for all mods in the manifest dictionary"""
    all_mods = set()
    for mod_line in manifest_dic.values():
        for mod in mod_line.values():
            all_mods.add(get_url_from_id(mod))
    return all_mods


def detail_mods(mod_details: dict, mod_urls: Set[str]) -> dict:
    """Update the given dictionary with the details for all the given mods based on
    their URLs
    """
    for mod_url in mod_urls:
        title = get_mod_title(mod_url)
        mod_details[get_id_from_url(mod_url)] = {
            "title": title,
            "updated": get_updated_date(mod_url),
            "directory_name": "@" + helpers.make_filename_safe(title),
        }
    return mod_details


def get_target_mod_details(manifest_url: str) -> dict:
    """Get new mod details dictionaries. This is used to check the date
    of the last update and get final dir names
    """
    click.echo("Collecting urls for all mods in mods manifest...")
    manifest_mod_urls = get_all_mods_manifest_urls(
        helpers.get_mods_manifest(manifest_url)
    )
    click.echo("Making sure all dependencies are accounted for...")
    all_mod_urls = collect_all_dependencies(manifest_mod_urls)
    target_mod_details = detail_mods(dict(), all_mod_urls)
    return target_mod_details
