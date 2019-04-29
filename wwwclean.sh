#!/bin/sh
# This script is run from /etc/cron.d/buildbot at 3am every day.
# This ensures that snapshots don't build up to the point of
# stopping builds due to out of disk space.

# Number of days to keep nightlies builds for.
# As this is 1 per day, this is approx the number of
# builds to keep as well (assuming no manual runs).
KEEP_N_DAYS=14

# Directory that snapshot builds are kept in.
SNAPSHOT_DIR=/.0/frs/snapshots/

# Iterate across snapshot directories, removing older builds..
# BUT skipping removal if they are the only remaining build.
for snapsubdir in `find ${SNAPSHOT_DIR} -type d`; do
	if [ ${snapsubdir} != ${SNAPSHOT_DIR} ]; then
		# If number of builds determined by native build name
		# is greater than 2, remove older ones ie. Just current and symlink
		# will be left
		NATIVE_BUILD="debian-x86-`basename ${snapsubdir}`"
		NUM_OF_BUILDS=`find ${snapsubdir}/${NATIVE_BUILD}-* | wc -l`
		if [ "${NUM_OF_BUILDS}" -gt 2 ]; then
			# Remove any files older than KEEP_N_DAYS
			find ${snapsubdir} -type f -mtime +${KEEP_N_DAYS} -delete
			# Remove any symbolic links older than KEEP_N_DAYS
			find ${snapsubdir} -type l -mtime +${KEEP_N_DAYS} -delete
		fi
	fi
done

# Remove any empty directories
find ${SNAPSHOT_DIR} -type d -empty -delete
