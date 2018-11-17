import pytest
from pathlib import Path

@pytest.mark.vcr()
def test_get_dependencies():
    """Test that dependency urls are received"""
    from update_mods import get_dependencies
    mod_ids = get_dependencies('https://steamcommunity.com/workshop/filedetails/?id=549676314')
    mod_ids.sort()
    assert mod_ids == [
        'https://steamcommunity.com/workshop/filedetails/?id=450814997',
        'https://steamcommunity.com/workshop/filedetails/?id=463939057',
        'https://steamcommunity.com/workshop/filedetails/?id=497660133'
    ]
    assert get_dependencies('https://steamcommunity.com/workshop/filedetails/?id=450814997') == []

def test_get_id_from_url():
    """Get id out of given url"""
    from update_mods import get_id_from_url
    assert get_id_from_url('https://steamcommunity.com/workshop/filedetails/?id=549676314') == '549676314'

def test_get_url_from_id():
    """Get url from id"""
    from update_mods import get_url_from_id
    assert get_url_from_id('549676314') == 'https://steamcommunity.com/workshop/filedetails/?id=549676314'

@pytest.mark.vcr()
def test_get_mod_title():
    """Make sure that the returned string is the title of the page"""
    from update_mods import get_mod_title
    assert get_mod_title('https://steamcommunity.com/workshop/filedetails/?id=549676314') ==\
                         'CUP ACE3 Compatibility Addon - Weapons'

@pytest.mark.vcr()
def test_collect_all_dependencies():
    """Get all mod dependencies and the mod itself"""
    from update_mods import collect_all_dependencies
    mod_line = [
        'https://steamcommunity.com/workshop/filedetails/?id=549676314',
        'https://steamcommunity.com/workshop/filedetails/?id=621650475'
    ]
    dependencies = {
        'https://steamcommunity.com/workshop/filedetails/?id=549676314',
        'https://steamcommunity.com/workshop/filedetails/?id=621650475',
        'https://steamcommunity.com/workshop/filedetails/?id=450814997',
        'https://steamcommunity.com/workshop/filedetails/?id=497660133',
        'https://steamcommunity.com/workshop/filedetails/?id=463939057',
        'https://steamcommunity.com/workshop/filedetails/?id=497661914',
        'https://steamcommunity.com/workshop/filedetails/?id=541888371'
    }
    assert collect_all_dependencies(mod_line) == dependencies

@pytest.mark.vcr()
def test_get_updated_date():
    """Test that the last updated date is returned, or posted date if that is not available"""
    from update_mods import get_updated_date
    assert get_updated_date('https://steamcommunity.com/workshop/filedetails/?id=450814997') == '11 Oct @ 11:05pm'
    # Mod with no update date (cTab at this time)
    assert get_updated_date('https://steamcommunity.com/workshop/filedetails/?id=871504836') == '24 Feb, 2017 @ 5:12pm'

@pytest.mark.vcr()
def test_get_all_mods_manifest():
    """Get a list of all mod urls in the given manifest url"""
    from update_mods import get_all_mods_manifest
    manifest_url = 'https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/mods_manifest.json'
    all_urls = {
        'https://steamcommunity.com/workshop/filedetails/?id=549676314',
        'https://steamcommunity.com/workshop/filedetails/?id=566942739',
        'https://steamcommunity.com/workshop/filedetails/?id=751965892',
        'https://steamcommunity.com/workshop/filedetails/?id=583496184',
        'https://steamcommunity.com/workshop/filedetails/?id=450814997',
        'https://steamcommunity.com/workshop/filedetails/?id=1555912648',
        'https://steamcommunity.com/workshop/filedetails/?id=909547724',
        'https://steamcommunity.com/workshop/filedetails/?id=508476583',
        'https://steamcommunity.com/workshop/filedetails/?id=820924072',
        'https://steamcommunity.com/workshop/filedetails/?id=497660133', 
        'https://steamcommunity.com/workshop/filedetails/?id=541888371',
        'https://steamcommunity.com/workshop/filedetails/?id=621650475',
        'https://steamcommunity.com/workshop/filedetails/?id=520618345',
        'https://steamcommunity.com/workshop/filedetails/?id=699630614',
        'https://steamcommunity.com/workshop/filedetails/?id=620260972',
        'https://steamcommunity.com/workshop/filedetails/?id=1291442929',
        'https://steamcommunity.com/workshop/filedetails/?id=871504836',
        'https://steamcommunity.com/workshop/filedetails/?id=583544987',
        'https://steamcommunity.com/workshop/filedetails/?id=1494115712',
        'https://steamcommunity.com/workshop/filedetails/?id=708250744',
        'https://steamcommunity.com/workshop/filedetails/?id=497661914',
        'https://steamcommunity.com/workshop/filedetails/?id=463939057'
    }
    assert get_all_mods_manifest(manifest_url) == all_urls

@pytest.mark.vcr()
def test_detail_all_mods():
    """Check that all given mod urls are fully detailed"""
    from update_mods import detail_all_mods
    details = {
        '450814997': {
            'title': 'CBA_A3',
            'updated': '11 Oct @ 11:05pm',
            'directory_name': '@cba_a3'
        },
        '463939057': {
            'title': 'ace',
            'updated': '9 Aug @ 8:43am',
            'directory_name': '@ace'
        }
    }
    mod_urls = {
        'https://steamcommunity.com/workshop/filedetails/?id=450814997',
        'https://steamcommunity.com/workshop/filedetails/?id=463939057'
    }
    assert detail_all_mods(mod_urls) == details

def test_make_filename_safe():
    """Check that the returned filename comes out as expected"""
    from update_mods import make_filename_safe
    assert make_filename_safe('cTab.pbo.Gundy.bisign') == 'ctab.pbo.gundy.bisign'
    assert make_filename_safe('[BW] Bush Wars v1.3 (Recce Challenge Addition)') ==\
                              'bw_bush_wars_v1.3_recce_challenge_addition'

def test_is_key_dir():
    """Check that it can figure out if the given path is a key directory"""
    from update_mods import is_key_dir
    assert is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys')
    assert is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys/')
    assert is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/Keys/')
    assert is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/Key/')
    assert is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/serverkey/')
    assert is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/ServerKeys')
    assert is_key_dir(Path('/Steam/steamapps/common/Arma 3/!Workshop/@ace/ServerKeys'))
    assert not is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys/addons')
    assert not is_key_dir('/Steam/steamapps/common/Arma 3/!Workshop/@ace/')
