#!/bin/sh
set -ex -o pipefail

/work/itests/setup.sh

if [[ -d "/ext/small" ]]; then
    cp -r /ext/small /small
else
    git clone https://github.com/yelp/paasta /small
fi
mkdir /large
if [[ -f "/ext/debian.iso" ]]; then
    cp /ext/debian.iso /large/
else
    wget -v https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-9.4.0-amd64-netinst.iso -O /large/debian.iso
fi

drop_init /small > /share/small
drop_init /large > /share/large

run_backend 0.0.0.0 2345 --external_address hostnode --backendonly
