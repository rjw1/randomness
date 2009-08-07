#!/usr/bin/bash
for db in london capetown vienna bobwiki circlewiki wpewiki cern rome
do
/usr/bin/pg_dump -Z 9 -f /export/home/bob/archivalbackups/$db.sql.`/usr/bin/date +%Y%m%d`.gz -d $db
done
/opt/csw/bin/svnadmin dump -q /export/home/repository/ | bzip2 > /export/home/bob/archivalbackups/svndump.`/usr/bin/date +%Y%m%d`.bz2
#backup up kakes a-z files
for file in a-to-z.txt a-to-z.kml a-to-z-pubs.txt a-to-z-pubs.kml
do
/opt/csw/bin/wget -O /export/home/bob/archivalbackups/$file.`/usr/bin/date +%Y%m%d` -q http://the.earth.li/~kake/misc/$file
done

