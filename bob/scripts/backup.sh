#!/usr/bin/bash


#backup up kakes a-z files
for file in a-to-z.txt a-to-z.kml a-to-z-pubs.txt a-to-z-pubs.kml 
do
wget -O /export/home/bob/backups/$file.`/usr/bin/date +%Y%m%d` -q http://the.earth.li/~kake/misc/$file
done

#backup up svn repo
svnadmin dump -q /export/home/subversion/randomness | bzip2 > /export/home/bob/backups/svndump.randomness.`/usr/bin/date +%Y%m%d`.bz2
svnadmin dump -q /export/home/subversion/secure | bzip2 > /export/home/bob/backups/svndump.secure.`/usr/bin/date +%Y%m%d`.bz2

# backup everything to rsync.net
rsync -az --exclude-from .rsync_exclude_list /export/home/bob/ ch-s010.rsync.net:nimbus/


