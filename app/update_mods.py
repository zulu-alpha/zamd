"""Module for updating a given mod folder and server key folder according to the given mods manifest"""
import os
import shutil
import json
from subprocess import run
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from pathlib import Path
import click
import requests
from bs4 import BeautifulSoup


STEAM_WORKHOP_PAGE_URL = 'https://steamcommunity.com/workshop/filedetails/'
MODS_DETAILS_PATH = 'mods_details.json'
MODLINES_PATH = 'modlines.json'
CACHE = {}

def get_dependencies(url):
    """Get steam workshop urls for all dependencies with the given mod's workshop url"""
    soup = BeautifulSoup(get_requests_object(url).text, 'html.parser')
    dependency_section = soup.find(id='RequiredItems')
    if dependency_section:
        return [link.get('href') for link in dependency_section.find_all('a')]
    return []

def get_requests_object(url):
    """Memoization for web requests"""
    if not url in CACHE:
        request = requests.get(url)
        assert request.status_code == 200
        CACHE[url] = request
    return CACHE[url]

def get_id_from_url(url):
    """Get the id from the standard steam URL for a workshop item"""
    return parse_qs(urlparse(url).query)['id'][0]

def get_url_from_id(mod_id):
    """Get the workshop URL for the given mod's workshop ID"""
    scheme, netloc, path, params, query, fragment = urlparse(STEAM_WORKHOP_PAGE_URL)
    query = urlencode({'id': mod_id})
    return urlunparse((scheme, netloc, path, params, query, fragment))

def get_mod_title(url):
    """Get the title for the given steamworkshop URL"""
    soup = BeautifulSoup(get_requests_object(url).text, 'html.parser')
    return soup.find_all('div', class_='workshopItemTitle')[0].contents[0]

def collect_all_dependencies(urls):
    """Return a set of all steamworkshop mod  (dependencies and given urls) needed to use all
    the mods in the url
    """
    url_set = set(urls)
    traversed_mods = set()
    for url in urls:
        recurse_dependencies(url, url_set, traversed_mods)
    return url_set

def recurse_dependencies(first_url, url_set, traversed_mods):
    """Recurse dependencies for given url and add to given set"""
    for url in get_dependencies(first_url):
        if not url in traversed_mods:
            traversed_mods.add(url)
            url_set.add(url)
            recurse_dependencies(url, url_set, traversed_mods)
    return url_set

def get_updated_date(url):
    """Get the string as it appears on the steamworkshop page of when it was last updated"""
    soup = BeautifulSoup(get_requests_object(url).text, 'html.parser')
    details_column = soup.find_all('div', class_='detailsStatRight')
    try:
        date = details_column[2].contents[0]
    except IndexError:
        date = details_column[1].contents[0]
    return date

def get_mods_manifest(manifest_url):
    """Get a dictionary of the manifest at the given URL"""
    return json.loads(get_requests_object(manifest_url).text)

def get_all_mods_manifest_urls(manifest_dic):
    """Return a set of urls for all mods in the manifest dictionary"""
    all_mods = set()
    for mod_line in manifest_dic.values():
        for mod in mod_line.values():
            all_mods.add(get_url_from_id(mod))
    return all_mods

def make_filename_safe(filename):
    """Return a unix safe version of the given filename"""
    safe_characters = (' ', '.', '_', '@')
    filename = ''.join(c for c in filename if c.isalnum() or c in safe_characters).rstrip()
    filename = filename.replace(' ', '_')
    return filename.lower()

def detail_mods(mod_details, mod_urls):
    """Update the given dictionary with the details for all the given mods based on their URLs"""
    for mod_url in mod_urls:
        title = get_mod_title(mod_url)
        mod_details[get_id_from_url(mod_url)] = {
            'title': title,
            'updated': get_updated_date(mod_url),
            'directory_name': '@' + make_filename_safe(title)
        }
    return mod_details

def is_key_dir(full_path):
    """Returns true if the given directory is likely to be a directory"""
    path = Path(full_path)
    dir_name = path.name.lower()
    return dir_name in ['key', 'keys', 'serverkey', 'serverkeys', 'server_key', 'server_keys']

def get_current_mod_details(mods_path):
    """Get a dictionary containing the current mod details."""
    mods_details_path = Path(mods_path, MODS_DETAILS_PATH)
    if mods_details_path.is_file():
        with open(mods_details_path) as open_file:
            mods_details = json.loads(open_file.read())
    else:
        mods_details = dict()
    return mods_details

def get_mod_details(manifest_url, mods_path):
    """Get new and old mod details json files. These files are used to check the date of the
    last update and get final dir names
    """
    click.echo('Collecting urls for all mods in mods manifest...')
    manifest_mod_urls = get_all_mods_manifest_urls(get_mods_manifest(manifest_url))
    click.echo('Making sure all dependencies are accounted for...')
    all_mod_urls = collect_all_dependencies(manifest_mod_urls)
    target_mod_details = detail_mods(dict(), all_mod_urls)
    current_mods_details = get_current_mod_details(mods_path)
    return target_mod_details, current_mods_details

def get_mods_to_download(target_mods_details, current_mods_details):
    """Figure out which mods"""
    return {
        mod_id for mod_id in target_mods_details if mod_id not in current_mods_details or \
        (mod_id in current_mods_details and current_mods_details[mod_id]['updated'] != target_mods_details[mod_id]['updated'])
    }

def download_steam_mod(mod_id, steamcmd_path, username, password, download_path):
    """Download the given steam mod using steamcmd. Return BOOL if failed."""
    code = -1
    counter = 0
    title = get_mod_title(get_url_from_id(mod_id))
    while code != 0 and counter < 3:
        counter += 1
        command = [
            steamcmd_path,
            '+@sSteamCmdForcePlatformType linux',
            '+login',
            username,
            password,
            '+force_install_dir',
            download_path,
            '+workshop_download_item',
            '107410',
            mod_id,
            'validate',
            '+quit'
        ]
        code = run(command).returncode
        if code != 0:
            click.echo(f'WARNING: Mod {title} download returned with code {code}!. Attempt {counter} of 3')
    if counter == 3:
        click.echo(f'ERROR: Mod {title} failed to download after 3 tries!')
        return False
    return True

def prepare_mod_dir(mod_id, downloaded_dir, destination_dir, mod_dir_name):
    """Rename the mod directory in the download folder and make sure the destination mod folder is clear of it"""
    shutil.rmtree(str(downloaded_dir / mod_dir_name), ignore_errors=True)
    os.rename(downloaded_dir / mod_id, downloaded_dir / mod_dir_name)
    shutil.rmtree(str(destination_dir / mod_dir_name), ignore_errors=True)

def make_files_or_dir_safe(parent, files_or_dirs):
    """Makes the given files or dirs in the given parent directory unix safe (lowercase, etc...)"""
    parent = Path(parent)
    for file_or_dir in files_or_dirs:
        safe_name = make_filename_safe(file_or_dir)
        os.rename(parent / file_or_dir, parent / safe_name)

def copy_keys(full_mod_path, keys_path):
    """Recursively search for the server key directory and copy it's keys to the destination directory.
    """
    full_mod_path = Path(full_mod_path)
    keys_path = Path(keys_path)
    key_copied = False
    for parent, _, files in os.walk(full_mod_path):
        parent = Path(parent)
        if is_key_dir(parent):
            for file_name in files:
                click.echo(f'Copying server key file {file_name} for: {full_mod_path.name}')
                if (keys_path / file_name).is_file():
                    os.remove(keys_path / file_name)
                shutil.copy2((parent / file_name), keys_path)
                key_copied = True
    if not key_copied:
        click.echo(f'WARNING: A server key for {full_mod_path.name} was not found!')

def make_files_and_dirs_safe(full_mod_path):
    """Recursively make all the file and directory names in the given directory safe for linux.
    """
    full_mod_path = Path(full_mod_path)
    # Do files and dirs separately as on linux renaming files could fail if parent dir is changed first
    for parent, _, files in os.walk(full_mod_path):
        make_files_or_dir_safe(parent, files)
    for parent, directories, _ in os.walk(full_mod_path):
        make_files_or_dir_safe(parent, directories)

def save_mods_details(mods_path, mods_details):
    """Save mods details to a json file at the given path"""
    with open(Path(mods_path, MODS_DETAILS_PATH), 'w') as open_file:
        open_file.write(json.dumps(mods_details))

def save_modlines(manifest_url, mods_details, mods_path):
    """Save a file that maps all mod folders to mod lines according to the manifest at the given URL"""
    mods_manifest = get_mods_manifest(manifest_url)
    modlines = dict()
    for modline in mods_manifest:
        mod_urls = collect_all_dependencies([
            get_url_from_id(mod_id) for mod_id in mods_manifest[modline].values()
        ])
        mod_ids = [get_id_from_url(mod_url) for mod_url in mod_urls]
        if set(mod_ids).difference(set(mods_details)):
            click.echo(f'WARNING: Not all mods for modline {modline} was downloaded, so it will be omitted!')
            continue
        modlines[modline] = [mods_details[mod_id]['directory_name'] for mod_id in mod_ids]
    with open(Path(mods_path, MODLINES_PATH), 'w') as open_file:
        open_file.write(json.dumps(modlines))

@click.command()
@click.option('--steamcmd_path', prompt='Path to steamcmd executable')
@click.option('--manifest_url', prompt='URL to raw manifest file')
@click.option('--download_path', prompt='Path to steam directory to download to')
@click.option('--mods_path', prompt='Path to directory to move mods to')
@click.option('--keys_path', prompt='Path to directory to put keys into')
@click.option('--username', prompt='Steam Username')
@click.option('--password', prompt='Steam Password')
def update_mods(steamcmd_path, manifest_url, download_path, mods_path, keys_path, username, password):
    """Updates mods according to the given mod line decalred in a mods_manifest.json file"""
    target_mod_details, current_mods_details = get_mod_details(manifest_url, mods_path)
    click.echo(f"Checking which of these mods to download: {[mod_details['title'] for mod_details in target_mod_details.values()]}...")
    to_download = get_mods_to_download(target_mod_details, current_mods_details)
    if to_download:
        click.echo(f"Only need to downloading: {[target_mod_details[mod_id]['title'] for mod_id in to_download]}...")
    else:
        return click.echo(f"No mods to download or update according to {Path(mods_path, MODS_DETAILS_PATH)}")
    for mod_id in to_download:
        click.echo(f"Downloading: {target_mod_details[mod_id]['title']}...")
        success = download_steam_mod(mod_id, steamcmd_path, username, password, download_path)
        if not success:
            continue
        downloaded_dir = Path(download_path, 'steamapps', 'workshop', 'content', '107410')
        destination_dir = Path(mods_path)
        mod_dir_name = target_mod_details[mod_id]['directory_name']
        click.echo(f"Making file and directory names safe: {target_mod_details[mod_id]['title']}...")
        prepare_mod_dir(mod_id, downloaded_dir, destination_dir, mod_dir_name)
        make_files_and_dirs_safe(downloaded_dir / mod_dir_name)
        click.echo(f"Checking for server keys to copy: {target_mod_details[mod_id]['title']}...")
        copy_keys(downloaded_dir / mod_dir_name, keys_path)
        click.echo(f'Moving the mod: {mod_dir_name} to destination...')
        shutil.move(str(downloaded_dir / mod_dir_name), str(destination_dir))
        current_mods_details = detail_mods(current_mods_details, [get_url_from_id(mod_id)])
        save_mods_details(mods_path, current_mods_details)
    save_modlines(manifest_url, current_mods_details, mods_path)

if __name__ == '__main__':
    update_mods()
                                                                               