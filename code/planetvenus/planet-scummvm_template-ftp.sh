#!/bin/sh
cd ~/planetvenus
echo "Running Planet Scripts"
python planet.py scummvm_template/config.ini
#echo "Sending Output via FTP"
#cd ~/www/planet
#echo "\$ planethourupload" | ftp -v ftps18.brinkster.com


