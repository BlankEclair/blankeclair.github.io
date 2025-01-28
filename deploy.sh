#!/bin/sh
set -xe
if [ "$(cat /etc/hostname)" != icecone ]; then
    exec ssh icecone /srv/http/claire/deploy.sh
fi

cd /srv/http/claire
git pull
. env/bin/activate
rm -r public
python3 generate.py
