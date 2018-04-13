#!/bin/sh
set -ex -o pipefail

node_init

make_dht_configs 2346 --bootstrap-peers 127.0.0.1:2346
