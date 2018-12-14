import pytest
import json
from pathlib import Path


@pytest.mark.vcr()
def test_get_dependencies():
    """Test that dependency urls are received"""
    from app.update_mods import get_dependencies

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
        get_dependencies(
            "https://steamcommunity.com/workshop/filedetails/?id=450814997"
        )
        == []
    )


def test_get_id_from_url():
    """Get id out of given url"""
    from app.update_mods import get_id_from_url

    assert (
        get_id_from_url("https://steamcommunity.com/workshop/filedetails/?id=549676314")
        == "549676314"
    )


def test_get_url_from_id():
    """Get url from id"""
    from app.update_mods import get_url_from_id

    assert (
        get_url_from_id("549676314")
        == "https://steamcommunity.com/workshop/filedetails/?id=549676314"
    )


@pytest.mark.vcr()
def test_get_mod_title():
    """Make sure that the returned string is the title of the page"""
    from app.update_mods import get_mod_title

    assert (
        get_mod_title("https://steamcommunity.com/workshop/filedetails/?id=549676314")
        == "CUP ACE3 Compatibility Addon - Weapons"
    )


@pytest.mark.vcr()
def test_collect_all_dependencies():
    """Get all mod dependencies and the mod itself"""
    from app.update_mods import collect_all_dependencies

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
    """Test that the last updated date is returned, or posted date if that is not available"""
    from app.update_mods import get_updated_date

    assert (
        get_updated_date(
            "https://steamcommunity.com/workshop/filedetails/?id=450814997"
        )
        == "11 Oct @ 11:05pm"
    )
    # Mod with no update date (cTab at this time)
    assert (
        get_updated_date(
            "https://steamcommunity.com/workshop/filedetails/?id=871504836"
        )
        == "24 Feb, 2017 @ 5:12pm"
    )


@pytest.mark.vcr()
def test_get_all_mods_manifest_urls():
    """Get a list of all mod urls in the given manifest url"""
    from app.update_mods import get_all_mods_manifest_urls, get_mods_manifest

    manifest_url = "https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/test_mods_manifest.json"
    all_urls = {
        "https://steamcommunity.com/workshop/filedetails/?id=333310405",
        "https://steamcommunity.com/workshop/filedetails/?id=871504836",
    }
    assert get_all_mods_manifest_urls(get_mods_manifest(manifest_url)) == all_urls


@pytest.mark.vcr()
def test_detail_mods():
    """Check that all given mod urls are fully detailed or appended to existing mods details"""
    from app.update_mods import detail_mods

    details = {
        "450814997": {
            "title": "CBA_A3",
            "updated": "11 Oct @ 11:05pm",
            "directory_name": "@cba_a3",
        },
        "463939057": {
            "title": "ace",
            "updated": "4 Dec @ 9:14am",
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
            "updated": "11 Oct @ 11:05pm",
            "directory_name": "@cba_a3",
        }
    }
    mod_urls = {
        "https://steamcommunity.com/workshop/filedetails/?id=450814997",
        "https://steamcommunity.com/workshop/filedetails/?id=463939057",
    }
    assert detail_mods(current_details, mod_urls) == details


def test_make_filename_safe():
    """Check that the returned filename comes out as expected"""
    from app.update_mods import make_filename_safe

    assert make_filename_safe("cTab.pbo.Gundy.bisign") == "ctab.pbo.gundy.bisign"
    assert (
        make_filename_safe("[BW] Bush Wars v1.3 (Recce Challenge Addition)")
        == "bw_bush_wars_v1.3_recce_challenge_addition"
    )


def test_is_key_dir():
    """Check that it can figure out if the given path is a key directory"""
    from app.update_mods import is_key_dir

    assert is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys")
    assert is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys/")
    assert is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/Keys/")
    assert is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/Key/")
    assert is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/serverkey/")
    assert is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/ServerKeys")
    assert is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/ServerKeys"))
    assert not is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys/addons")
    assert not is_key_dir("/Steam/steamapps/common/Arma 3/!Workshop/@ace/")


@pytest.mark.vcr()
def test_save_modlines(tmp_path):
    """Check that all the correct mod dir names are written to the file"""
    from app.update_mods import save_modlines, MODLINES_PATH

    manifest_url = "https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/test_mods_manifest.json"
    mods_details = {
        "450814997": {
            "title": "CBA_A3",
            "updated": "11 Oct @ 11:05pm",
            "directory_name": "@cba_a3",
        },
        "333310405": {
            "title": "Enhanced Movement",
            "updated": "10 May @ 11:01am",
            "directory_name": "@enhanced_movement",
        },
        "871504836": {
            "title": "cTab V2.2.1",
            "updated": "24 Feb, 2017 @ 5:12pm",
            "directory_name": "@ctab_v2.2.1",
        },
    }
    save_modlines(manifest_url, mods_details, str(tmp_path))
    with open(tmp_path / MODLINES_PATH, "r") as open_file:
        modlines = json.loads(open_file.read())
        assert "main" in modlines and "recce" in modlines
        assert "@cba_a3" in modlines["main"] and "@ctab_v2.2.1" in modlines["main"]
        assert "@enhanced_movement" in modlines["recce"]
