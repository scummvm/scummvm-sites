#!/bin/bash

LOCKDIR=/data/scummvm/gitmailer/gitlock
REPO=/data/scummvm/gitmailer/repo
GIT=/usr/bin/git

while ! mkdir $LOCKDIR; do
  sleep 3
done

if [ ! -n "$1" ]
then
  exit 0
fi
if [ ! -n "$2" ]
then
  exit 0
fi

REPONAME=$1
REV=$2

if [ ! -d "$REPO/$REPONAME" ]
then
  exit 0
fi

cd "$REPO/$REPONAME"
$GIT fetch -a -q > /dev/null
$GIT show --format="format:" $REV | head -n 10000

rmdir $LOCKDIR
