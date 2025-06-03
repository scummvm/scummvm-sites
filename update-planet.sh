eval "$(/var/www/.rbenv/bin/rbenv init -)"

rbenv global 3.4.4

cd /var/www/pluto

pluto build /var/www/pluto/planet.ini -t scummvm -o /var/www/pluto/public_html
