#!/usr/bin/bash
for db in london capetown vienna bobwiki circlewiki wpewiki cern
do
/usr/bin/pg_dump -Z 9 -f /export/home/bob/backups/$db.sql.`/usr/bin/date +%Y%m%d`.gz -d $db
done
/opt/csw/bin/svnadmin dump -q /export/home/repository/ | bzip2 > /export/home/bob/backups/svndump.`/usr/bin/date +%Y%m%d`.bz2
/opt/csw/bin/rsync -aqz --exclude-from .rsync_exclude_list /export/home/bob/ theproject.fierypit.org:nebulabackup/
/opt/csw/bin/rsync -aqz --exclude-from .rsync_exclude_list /export/home/bob/ ch-s010.rsync.net:nebula/
cp /export/home/bob/backups/london.sql.`/usr/bin/date +%Y%m%d`.gz /export/home/bob/web/vhosts/london.randomness.org.uk/dbdump/rgl.sql.gz
cp /export/home/bob/backups/vienna.sql.`/usr/bin/date +%Y%m%d`.gz /export/home/bob/web/vhosts/vienna.openguides.org/dbdump/vienna.sql.gz
