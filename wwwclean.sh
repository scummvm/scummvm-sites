#!/bin/sh
# This script is run from /etc/cron.d/buildbot at 3am every day.
# This ensures that snapshots don't build up to the point of
# stopping builds due to out of disk space.

# Number of days to keep nightlies builds for.
# As this is 1 per day, this is approx the number of
# builds to keep as well (assuming no manual runs).
KEEP_N_DAYS=7
# FIXME - Need to ensure that in the event that older build is the
# only build, they are not removed i.e. nightlies are not rebuilt
# if not commits have been made during that day, so 7 days of no
# commits means the snapshot is removed :/
# This has occurred for stable builds and should be avoided...
# Somehow...
find /var/www/snapshots/ -type f -mtime +${KEEP_N_DAYS} -delete
find /var/www/snapshots/ -type l -mtime +${KEEP_N_DAYS} -delete
find /var/www/snapshots/ -type d -empty -delete

