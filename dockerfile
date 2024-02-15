FROM ubuntu:bionic

LABEL maintainer="adam@piskorski.me"

ARG STEAM_USERNAME
ARG STEAM_PASSWORD

RUN apt-get update &&  \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y lib32gcc1 && \
    apt-get install -y wget && \
    apt-get install -y python3.7 python3.7-dev libncurses5-dev && \
    python3.7 get-pip.py && \
    rm get-pip.py

WORKDIR /mod_updater
COPY app/ /mod_updater
COPY Pipfile Pipfile.lock /mod_updater/
RUN pip3 install pipenv && \
    pipenv install --ignore-pipfile

WORKDIR /steamcmd
RUN wget -qO- "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -

RUN mkdir /downloads && \
    mkdir /mods && \
    mkdir keys

ENTRYPOINT ["pipenv", "run", "python3", "run.py"]

# pipenv run python update_mods.py --steamcmd_path C:\Users\adam\temp\zags\steamcmd\steamcmd.exe --manifest_url https://raw.githubusercontent.com/zulu-alpha/mod-lines/master/test_mods_manifest.json --download_path C:\Users\adam\temp\zags\ --mods_path C:\Users\adam\temp\zags\mods --keys_path C:\Users\adam\temp\zags\keys --username ZuluAlpha_coza --password 31FZ53NR21k4jUOo6Gpf