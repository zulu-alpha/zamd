"""Functions for files on the system"""
import os
import shutil
import json
from pathlib import Path
from typing import List
import click
from app import steam_site, helpers


MODS_DETAILS_FILENAME = "mods_details.json"
MODLINES_FILENAME = "modlines.json"


def get_current_mod_details(mods_path: Path) -> dict:
    """Get a dictionary containing the current mod details."""
    mods_details_path = mods_path / MODS_DETAILS_FILENAME
    if mods_details_path.is_file():
        with open(mods_details_path) as open_file:
            mods_details = json.loads(open_file.read())
    else:
        mods_details = dict()
    return mods_details


def is_key_dir(full_path: Path) -> bool:
    """Returns true if the given directory is likely to be a directory for keys"""
    dir_name = full_path.name.lower()
    return dir_name in [
        "key",
        "keys",
        "serverkey",
        "serverkeys",
        "server_key",
        "server_keys",
    ]


def copy_keys(full_mod_path: Path, keys_path: Path) -> None:
    """Recursively search for the server key directory and copy it's keys to the
    destination directory.
    """
    key_copied = False
    for parent, _, files in os.walk(full_mod_path):
        parent_path = Path(parent)
        if is_key_dir(parent_path):
            for file_name in files:
                click.echo(
                    f"Copying server key file {file_name} for: {full_mod_path.name}"
                )
                if (keys_path / file_name).is_file():
                    os.remove(keys_path / file_name)
                shutil.copy2((parent_path / file_name), keys_path)
                key_copied = True
    if not key_copied:
        click.echo(f"WARNING: A server key for {full_mod_path.name} was not found!")


def prepare_mod_dir(
    mod_id: str, downloaded_dir: Path, destination_dir: Path, mod_dir_name: str
) -> None:
    """Rename the mod directory in the download folder and make sure the destination
    mod folder is clear of it
    """
    shutil.rmtree(str(downloaded_dir / mod_dir_name), ignore_errors=True)
    os.rename(downloaded_dir / mod_id, downloaded_dir / mod_dir_name)
    shutil.rmtree(str(destination_dir / mod_dir_name), ignore_errors=True)


def rename_to_safe(parent: str, files_or_dirs: List[str]) -> None:
    """Makes the given files or dirs in the given parent directory unix safe
    eg: lowercase, etc...
    """
    parent_path = Path(parent)
    for file_or_dir in files_or_dirs:
        safe_name = helpers.make_filename_safe(file_or_dir)
        os.rename(parent_path / file_or_dir, parent_path / safe_name)


def make_files_and_dirs_safe(full_mod_path: Path) -> None:
    """Recursively make all the file and directory names in the given directory safe for
    linux.
    """
    # Do files and dirs separately as on linux renaming files could fail if parent dir
    # is changed first.
    for parent, _, files in os.walk(full_mod_path):
        rename_to_safe(parent, files)
    for parent, directories, _ in os.walk(full_mod_path):
        rename_to_safe(parent, directories)


def save_mods_details(mods_path: str, mods_details: dict) -> None:
    """Save mods details to a json file at the given path"""
    with open(Path(mods_path, MODS_DETAILS_FILENAME), "w") as open_file:
        open_file.write(json.dumps(mods_details))


def save_modlines(manifest_url: str, mods_details: dict, mods_path: str) -> None:
    """Save a file that maps all mod folders to mod lines according to the manifest at
    the given URL
    """
    mods_manifest = helpers.get_mods_manifest(manifest_url)
    modlines = dict()
    for modline in mods_manifest:
        mod_urls = steam_site.collect_all_dependencies(
            {
                steam_site.get_url_from_id(mod_id)
                for mod_id in mods_manifest[modline].values()
            }
        )
        mod_ids = {steam_site.get_id_from_url(mod_url) for mod_url in mod_urls}
        if mod_ids.difference(set(mods_details)):
            click.echo(
                (
                    f"WARNING: Not all mods for modline {modline} was downloaded, "
                    f"so it will be omitted!"
                )
            )
            continue
        modlines[modline] = [mods_details[mod_id]["directory_name"] for mod_id in mod_ids]
    with open(Path(mods_path, MODLINES_FILENAME), "w") as open_file:
        open_file.write(json.dumps(modlines))
