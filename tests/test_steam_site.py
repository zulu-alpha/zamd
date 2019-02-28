"""Tests for steam site functions"""
import pytest  # type: ignore


@pytest.mark.vcr()
def test_get_dependencies():
    """Test that dependency urls are received"""
    from app.steam_site import get_dependencies

    mod_ids = get_dependencies(
        "https://steamcommunity.com/workshop/filedetails/?id=549676314"
    )
    mod_ids.sort()
    assert mod_ids == [
        "https://steamcommunity.com/workshop/filedetails/?id=450814997",
        "https://steamcommunity.com/workshop/filedetails/?id=463939057",
        "https://steamcommunity.com/workshop/filedetails/?id=497660133",
    ]
    assert (
        get_dependencies("https://steamcommunity.com/workshop/filedetails/?id=450814997")
        == []
    )


def test_get_id_from_url():
    """Get id out of given url"""
    from app.steam_site import get_id_from_url

    assert (
        get_id_from_url("https://steamcommunity.com/workshop/filedetails/?id=549676314")
        == "549676314"
    )


def test_get_url_from_id():
    """Get url from id"""
    from app.steam_site import get_url_from_id

    assert (
        get_url_from_id("549676314")
        == "https://steamcommunity.com/workshop/filedetails/?id=549676314"
    )


@pytest.mark.vcr()
def test_get_mod_title():
    """Make sure that the returned string is the title of the page"""
    from app.steam_site import get_mod_title

    assert (
        get_mod_title("https://steamcommunity.com/workshop/filedetails/?id=549676314")
        == "CUP ACE3 Compatibility Addon - Weapons"
    )


@pytest.mark.vcr()
def test_collect_all_dependencies():
    """Get all mod dependencies and the mod itself"""
    from app.steam_site import collect_all_dependencies

    mod_line = [
        "https://steamcommunity.com/workshop/filedetails/?id=549676314",
        "https://steamcommunity.com/workshop/filedetails/?id=621650475",
    ]
    dependencies = {
        "https://steamcommunity.com/workshop/filedetails/?id=549676314",
        "https://steamcommunity.com/workshop/filedetails/?id=621650475",
        "https://steamcommunity.com/workshop/filedetails/?id=450814997",
        "https://steamcommunity.com/workshop/filedetails/?id=497660133",
        "https://steamcommunity.com/workshop/filedetails/?id=463939057",
        "https://steamcommunity.com/workshop/filedetails/?id=497661914",
        "https://steamcommunity.com/workshop/filedetails/?id=541888371",
    }
    assert collect_all_dependencies(mod_line) == dependencies


@pytest.mark.vcr()
def test_get_updated_date():
    """Test that the last updated date is returned, or posted date if that is not
    available
    """
    from app.steam_site import get_updated_date

    assert (
        get_updated_date("https://steamcommunity.com/workshop/filedetails/?id=450814997")
        == "10 Jan @ 7:24am"
    )
    # Mod with no update date (cTab at this time)
    assert (
        get_updated_date("https://steamcommunity.com/workshop/filedetails/?id=871504836")
        == "24 Feb, 2017 @ 5:12pm"
    )


@pytest.mark.vcr()
def test_get_all_mods_manifest_urls():
    """Get a list of all mod urls in the given manifest url"""
    from app.steam_site import get_all_mods_manifest_urls
    from app.helpers import get_mods_manifest

    manifest_url = (
        "https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/"
        "test_mods_manifest.json"
    )
    all_urls = {
        "https://steamcommunity.com/workshop/filedetails/?id=333310405",
        "https://steamcommunity.com/workshop/filedetails/?id=871504836",
    }
    assert get_all_mods_manifest_urls(get_mods_manifest(manifest_url)) == all_urls


@pytest.mark.vcr()
def test_detail_mods():
    """Check that all given mod urls are fully detailed or appended to existing mods
    details
    """
    from app.steam_site import detail_mods

    details = {
        "450814997": {
            "title": "CBA_A3",
            "updated": "10 Jan @ 7:24am",
            "directory_name": "@cba_a3",
        },
        "463939057": {
            "title": "ace",
            "updated": "4 Dec, 2018 @ 9:14am",
            "directory_name": "@ace",
        },
    }
    mod_urls = {
        "https://steamcommunity.com/workshop/filedetails/?id=450814997",
        "https://steamcommunity.com/workshop/filedetails/?id=463939057",
    }
    assert detail_mods(dict(), mod_urls) == details

    current_details = {
        "450814997": {
            "title": "CBA_A3",
            "updated": "10 Jan @ 7:24am",
            "directory_name": "@cba_a3",
        }
    }
    mod_urls = {
        "https://steamcommunity.com/workshop/filedetails/?id=450814997",
        "https://steamcommunity.com/workshop/filedetails/?id=463939057",
    }
    assert detail_mods(current_details, mod_urls) == details
