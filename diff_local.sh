#!/bin/bash

LOCKDIR=/var/www/git-diff-mailer/scummvm/gitlock
GIT=/usr/bin/git

#while ! mkdir $LOCKDIR; do
#  sleep 3
#done

#if [ ! -n "$1" ]
#then
#  rmdir $LOCKDIR
#  exit 0
#fi
#if [ ! -n "$2" ]
#then
#  rmdir $LOCKDIR
#  exit 0
#fi

REPONAME=$1
REPO=/var/www/git-diff-mailer/$REPONAME/repo
REV=$2

#if [ ! -d "$REPO/$REPONAME" ]
#then
#  rmdir $LOCKDIR
#  exit 0
#fi

cd "$REPO"
/usr/bin/git -C $REPO fetch -q origin '+refs/heads/*:refs/remotes/origin/*' > /dev/null
/usr/bin/git -C $REPO show --format="format:" $REV | head -n 10000
/usr/bin/git -C $REPO gc --auto --quiet > /dev/null

rmdir $LOCKDIR
