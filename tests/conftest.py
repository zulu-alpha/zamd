import pytest
from pathlib import Path


MODS_DETAILS = {
    "450814997": {
        "title": "CBA_A3",
        "updated": "10 Jan @ 7:24am",
        "directory_name": "@cba_a3",
    },
    "333310405": {
        "title": "Enhanced Movement",
        "updated": "10 May, 2018 @ 11:01am",
        "directory_name": "@enhanced_movement",
    },
    "871504836": {
        "title": "cTab",
        "updated": "24 Feb, 2017 @ 5:12pm",
        "directory_name": "@ctab",
    },
}
MOD_ID_KEY_PAIRS = {"450814997": "Key", "333310405": "Keys", "871504836": "Serverkey"}


@pytest.fixture()
def source_mods(tmp_path: Path) -> Path:
    """Create a simulated Steam Workshop download directory"""
    workshop_dir = tmp_path / "107410"
    workshop_dir.mkdir()
    for mod_id in MODS_DETAILS:
        mod_dir = workshop_dir / mod_id
        some_file = mod_dir / "Readme #@-12.TXT"
        addon_dir = mod_dir / "Addons"
        addon = addon_dir / "Junk File-$ 1.1.pbo"
        key_dir = mod_dir / MOD_ID_KEY_PAIRS[mod_id]
        key = key_dir / "Some Key.BiKEY"
        for p in [mod_dir, addon_dir, key_dir]:
            p.mkdir()
        addon.write_text("some mod junk")
        key.write_text("some key junk")
        some_file.write_text("junk")
    return workshop_dir


@pytest.fixture()
def empty_destination(tmp_path: Path) -> Path:
    """Creates a clean destination mod dir"""
    destination = tmp_path / "mods"
    destination.mkdir()
    return destination
