#!/bin/bash
# script to set up backups for a wen user.

# make backup dir structure
mkdir -p ~/backups/{weekly,daily,monthly}/{db,files}
cp -r ~rgl/backups/scripts ~/backups
vi ~/backups/scripts/daily.sh
vi ~/backups/scripts/weekly.sh
vi ~/backups/scripts/monthly.sh

ssh-keygen -t rsa

cat ~/.ssh/id_rsa.pub | ssh bob@hetzner.barnyard.co.uk "cat >> ~/.ssh/authorized_keys"

~/backups/scripts/daily.sh
~/backups/scripts/weekly.sh
~/backups/scripts/monthly.sh

crontab -e 
