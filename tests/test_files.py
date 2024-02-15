"""Test file specific functions"""
import json
from pathlib import Path
import pytest


def test_get_current_mod_details():
    """Test that it can properly open the details file or make a new dict"""
    assert False


def test_is_key_dir():
    """Check that it can figure out if the given path is a key directory"""
    from app.files import is_key_dir

    assert is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys"))
    assert is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys/"))
    assert is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/Keys/"))
    assert is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/Key/"))
    assert is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/serverkey/"))
    assert is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/ServerKeys"))
    assert not is_key_dir(
        Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/keys/addons")
    )
    assert not is_key_dir(Path("/Steam/steamapps/common/Arma 3/!Workshop/@ace/"))


def test_copy_keys():
    assert False


def test_prepare_mod_dir():
    assert False


def test_save_mods_details():
    assert False


def test_make_files_and_dirs_safe(source_mods, empty_destination):
    """Test that files and directories are renamed to linux safe names"""
    from app.files import make_files_and_dirs_safe, prepare_mod_dir
    from tests.conftest import MOD_ID_KEY_PAIRS, MODS_DETAILS

    for mod_id, details in MODS_DETAILS.items():
        prepare_mod_dir(mod_id, source_mods, empty_destination, details["directory_name"])

    make_files_and_dirs_safe(source_mods)
    for mod_id, key_dir_name in MOD_ID_KEY_PAIRS.items():
        mod_dir = source_mods / MODS_DETAILS[mod_id]["directory_name"]
        assert mod_dir / "readme_12.txt"
        assert (mod_dir / "addons").is_dir()
        assert (mod_dir / "addons" / "junk_file_1.1.pbo").is_file()
        assert (mod_dir / key_dir_name.lower()).is_dir()
        assert (mod_dir / key_dir_name.lower() / "some_key.bikey").is_file()


@pytest.mark.vcr()
def test_save_modlines(tmp_path):
    """Check that all the correct mod dir names are written to the file"""
    from app.files import save_modlines, MODLINES_FILENAME
    from tests.conftest import MODS_DETAILS

    manifest_url = (
        "https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/"
        "test_mods_manifest.json"
    )
    save_modlines(manifest_url, MODS_DETAILS, str(tmp_path))
    with open(tmp_path / MODLINES_FILENAME, "r") as open_file:
        modlines = json.loads(open_file.read())
        assert "main" in modlines and "recce" in modlines
        assert "@cba_a3" in modlines["main"] and "@ctab" in modlines["main"]
        assert "@enhanced_movement" in modlines["recce"]
