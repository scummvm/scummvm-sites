#!/bin/sh
cd ~buildbot/.android
mv -v debug.keystore debug.keystore-`date +%Y-%m-%d`
#Make Android Debug Key Valid for 1 year
keytool -genkey -v -keystore ./debug.keystore \
-storepass android -alias androiddebugkey -keypass android \
-dname "CN=Android Debug,O=Android,C=US" \
-validity 365 \
-keysize 1024
chown buildbot:nogroup debug.keystore
