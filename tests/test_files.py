"""Test file specific functions"""
import json
from pathlib import Path
import pytest  # type: ignore


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


@pytest.mark.vcr()
def test_save_modlines(tmp_path):
    """Check that all the correct mod dir names are written to the file"""
    from app.files import save_modlines, MODLINES_FILENAME

    manifest_url = (
        "https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/"
        "test_mods_manifest.json"
    )
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
    with open(tmp_path / MODLINES_FILENAME, "r") as open_file:
        modlines = json.loads(open_file.read())
        assert "main" in modlines and "recce" in modlines
        assert "@cba_a3" in modlines["main"] and "@ctab_v2.2.1" in modlines["main"]
        assert "@enhanced_movement" in modlines["recce"]
