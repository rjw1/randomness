#!/usr/bin/bash

#backup local databases
for db in london capetown vienna bobwiki circlewiki wpewiki cern rome
do
/usr/bin/pg_dump -Z 9 -f /export/home/bob/backups/$db.sql.`/usr/bin/date +%Y%m%d`.gz -d $db
done

#backup up kakes a-z files
for file in a-to-z.txt a-to-z.kml a-to-z-pubs.txt a-to-z-pubs.kml 
do
/opt/csw/bin/wget -O /export/home/bob/backups/$file.`/usr/bin/date +%Y%m%d` -q http://the.earth.li/~kake/misc/$file
done

#backup up svn repo
/opt/csw/bin/svnadmin dump -q /export/home/repository/ | bzip2 > /export/home/bob/backups/svndump.`/usr/bin/date +%Y%m%d`.bz2

# backup everything to rsync.net
/opt/csw/bin/rsync -az --exclude-from .rsync_exclude_list /export/home/bob/ ch-s010.rsync.net:nebula/

# backup up rgl db to dave's  box
/opt/csw/bin/rsync  /export/home/bob/backups/london.sql.`/usr/bin/date +%Y%m%d`.gz hetzner.barnyard.co.uk:rglbackup/ 

# copy db dumps to web accessabel locations for others to use.
cp /export/home/bob/backups/london.sql.`/usr/bin/date +%Y%m%d`.gz /export/home/bob/web/vhosts/london.randomness.org.uk/dbdump/rgl.sql.gz
cp /export/home/bob/backups/vienna.sql.`/usr/bin/date +%Y%m%d`.gz /export/home/bob/web/vhosts/vienna.openguides.org/dbdump/vienna.sql.gz

# remove any backup older than 7 days. 
find /export/home/bob/backups/ -mtime +7 -exec mv {} /export/home/bob/oldbackups/ \;
