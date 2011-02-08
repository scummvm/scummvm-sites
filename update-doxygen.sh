#!/bin/sh -ev

BASEPATH=/home/joostp/doxygen

source ${BASEPATH}/lock_unlock

LOCKFILE=${BASEPATH}/doxygen.lock

# Create a lockfile (and delete it if we abort)
lock_unlock action=lock name=$LOCKFILE

# TODO: Verify that the SVN checkout exists, is valid, etc.
# And if it is not, we might be able to automatically recreate it...
echo "Updating SVN..."
cd ${BASEPATH}/scummvm-SVN-trunk
nice svn up

#echo "Fixing permissions in the checkout"
#chmod -f -R g+w,a+r .
#chgrp -R scummvm .

echo Updating doxygen docs
cd ${BASEPATH}
nice doxygen config

# Fix the index.html file <title> if necessary
perl -pi -e 's,<title>ScummVM</title>,<title>ScummVM :: Doxygen</title>,g' /var/www/doxygen/html/index.html

#echo "Fixing permissions"
#chmod -f -R g+w,a+r .
#chgrp -R scummvm .

lock_unlock action=unlock name=$LOCKFILE
