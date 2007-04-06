#!/usr/bin/bash
for db in london capetown
do
/usr/bin/pg_dump -Z 9 -f /export/home/bob/backups/$db.sql.`/usr/bin/date +%Y%m%d`.gz -d $db
done
/opt/csw/bin/svnadmin dump -q /export/home/repository/ | bzip2 > /export/home/bob/backups/svndump.`/usr/bin/date +%Y%m%d`.bz2
/opt/csw/bin/rsync -aqz /export/home/bob/ theproject.fierypit.org:nebulabackup/
