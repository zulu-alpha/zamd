FROM python:3.7 as build

LABEL maintainer="adam@piskorski.me"

RUN apt-get update &&  \
    apt-get install -y lib32gcc1 && \
    apt-get install -y wget

WORKDIR /steamcmd
RUN wget -qO- "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -

WORKDIR /mod_updater
COPY . /mod_updater

RUN python3 -m pip install pipenv
RUN pipenv install --ignore-pipfile

ENTRYPOINT ["pipenv", "run", "python3", "update_mods.py", "--steamcmd_path=/steamcmd/steamcmd.sh", "--path=/mods"]
