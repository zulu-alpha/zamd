"""Module for updating a given mod folder and server key folder according to the given
mods manifest
"""
import shutil
from subprocess import run
from pathlib import Path
from typing import List, Set
import click
from app import steam_site, files


def get_mods_to_download(new_mods_details: dict, current_mods_details: dict) -> Set[str]:
    """Figure out which mods to download based on date and prior existence"""
    return {
        mod_id
        for mod_id in new_mods_details
        if mod_id not in current_mods_details
        or (
            mod_id in current_mods_details
            and current_mods_details[mod_id]["updated"]
            != new_mods_details[mod_id]["updated"]
        )
    }


def download_steam_mod(
    mod_id: str, steamcmd_path: Path, username: str, password: str, download_path: Path
) -> bool:
    """Download the given steam mod using steamcmd. Return BOOL if failed."""
    code = -1
    counter = 0
    title = steam_site.get_mod_title(steam_site.get_url_from_id(mod_id))
    while code != 0 and counter < 3:
        counter += 1
        command: List[str] = [
            str(steamcmd_path),
            "+@sSteamCmdForcePlatformType linux",
            "+login",
            username,
            password,
            "+force_install_dir",
            str(download_path),
            "+workshop_download_item",
            "107410",
            mod_id,
            "validate",
            "+quit",
        ]
        code = run(command).returncode
        if code != 0:
            click.echo(
                (
                    f"WARNING: Mod {title} download returned with code {code}! "
                    f"Attempt {counter} of 3"
                )
            )
    if counter == 3:
        click.echo(f"ERROR: Mod {title} failed to download after 3 tries!")
        return False
    return True


@click.command()
@click.option("--steamcmd_path", prompt="Path to steamcmd executable")
@click.option("--manifest_url", prompt="URL to raw manifest file")
@click.option("--download_path", prompt="Path to steam directory to download to")
@click.option("--mods_path", prompt="Path to directory to move mods to")
@click.option("--keys_path", prompt="Path to directory to put keys into")
@click.option("--username", prompt="Steam Username")
@click.option("--password", prompt="Steam Password")
def update_mods(
    steamcmd_path, manifest_url, download_path, mods_path, keys_path, username, password
):
    """Updates mods according to the given mod line decalred in a mods_manifest.json
    file
    """
    new_mod_details = steam_site.get_all_manifest_mods_details(manifest_url)
    current_mods_details = files.get_current_mod_details(mods_path)
    click.echo(
        (
            "Checking which of these mods to download: "
            f"{[mod_details['title'] for mod_details in new_mod_details.values()]}..."
        )
    )
    to_download = get_mods_to_download(new_mod_details, current_mods_details)
    if to_download:
        click.echo(
            (
                "Only need to downloading: "
                f"{[new_mod_details[mod_id]['title'] for mod_id in to_download]}..."
            )
        )
    else:
        click.echo(
            (
                "No mods to download or update according to "
                f"{Path(mods_path, files.MODS_DETAILS_FILENAME)}"
            )
        )
        return 1
    for mod_id in to_download:
        click.echo(f"Downloading: {new_mod_details[mod_id]['title']}...")
        success = download_steam_mod(
            mod_id, steamcmd_path, username, password, download_path
        )
        if not success:
            continue
        downloaded_dir = Path(download_path, "steamapps", "workshop", "content", "107410")
        destination_dir = Path(mods_path)
        mod_dir_name = new_mod_details[mod_id]["directory_name"]
        click.echo(
            (
                "Making file and directory names safe: "
                f"{new_mod_details[mod_id]['title']}..."
            )
        )
        files.prepare_mod_dir(mod_id, downloaded_dir, destination_dir, mod_dir_name)
        files.make_files_and_dirs_safe(downloaded_dir / mod_dir_name)
        click.echo(
            f"Checking for server keys to copy: {new_mod_details[mod_id]['title']}..."
        )
        files.copy_keys(downloaded_dir / mod_dir_name, Path(keys_path))
        click.echo(f"Moving the mod: {mod_dir_name} to destination...")
        shutil.move(str(downloaded_dir / mod_dir_name), str(destination_dir))
        current_mods_details = steam_site.detail_mods(
            current_mods_details, [steam_site.get_url_from_id(mod_id)]
        )
        files.save_mods_details(mods_path, current_mods_details)
    files.save_modlines(manifest_url, current_mods_details, mods_path)
    return 1


if __name__ == "__main__":
    update_mods()  # pylint: disable=E1120
