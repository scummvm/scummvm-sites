#!/usr/bin/env bash

# settings exit on:
# -e: non zero exit code,
# -u: an undefined variable
# pipefile: return exit code of last command in the pipe
set -euo pipefail

LOGFILE=run.txt
HOST=test-buildbot
DOMAIN=projecttycho.nl

# create and wait for droplet to come up
doctl compute droplet create test-deploy \
    --enable-monitoring \
    --image ubuntu-20-04-x64 \
    --size s-1vcpu-1gb \
    --region ams3 \
    --user-data-file cloudinit.sh \
    --ssh-keys 27:98:ce:25:93:79:5a:9e:d6:46:94:10:07:5f:a6:fd \
    --format ID \
    --wait \
    > $LOGFILE

# get droplet ID
DO_ID=`tail -1 $LOGFILE`

# get droplet IP address
doctl compute droplet get $DO_ID \
    --format PublicIPv4 \
    >> $LOGFILE
DO_IP=`tail -1 $LOGFILE`

# create POST body for Transip via jq.
# In bash it's not possible to use $VARs in single quoted strings
POST_JSON=`jq -n --arg host "$HOST"--arg ip "$DO_IP" \
'{
  "dnsEntry": {
    "name": $host,
    "expire": 60,
    "type": "A",
    "content": $ip
  }
}'`

curl -X PATCH \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $BEARER" \
    -d "$POST_JSON" \
    "https://api.transip.nl/v6/domains/$DOMAIN/dns" \
    >> $LOGFILE

# Be able to login without SSH complaining
ssh-keygen -f ~/.ssh/known_hosts -R "$HOST.$DOMAIN"
