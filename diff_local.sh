#!/bin/bash

LOCKDIR=/home/mozzie/gitlock
REPO=/home/mozzie/svm/
GIT=/usr/bin/git

while ! mkdir $LOCKDIR; do
  sleep 3
done

if [ ! -n "$1" ]
then
  exit 0
fi

REV=$1

cd $REPO
$GIT fetch -a > /dev/null
$GIT diff -p --no-color  $REV~1..$REV --

rmdir $LOCKDIR
