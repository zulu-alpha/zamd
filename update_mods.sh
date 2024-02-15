#!/bin/sh
# Example shell script used on ZA server.
pipenv run python /home/adam/zamd/app/update_mods.py --steamcmd /home/adam/steamcmd.sh --manifest_url https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/mods_manifest.json --download_path /home/adam/downloads --mods_path /home/adam/arma3/mods --keys_path /home/adam/arma3/keys --username $STEAM_USERNAME --password $STEAM_PASSWORD