#!/usr/bin/bash


#backup up kakes a-z files
for file in a-to-z.txt a-to-z.kml a-to-z-pubs.txt a-to-z-pubs.kml 
do
wget -O /export/home/bob/backups/weekly/$file.`/usr/bin/date +%Y%m%d` -q http://the.earth.li/~kake/misc/$file
touch /export/home/bob/backups/weekly/$file.`/usr/bin/date +%Y%m%d`
gzip /export/home/bob/backups/weekly/$file.`/usr/bin/date +%Y%m%d`
done

#backup up svn repos
for repo in randomness secure bob
do
svnadmin dump -q /export/home/subversion/$repo | bzip2 > /export/home/bob/backups/weekly/svndump.$repo.`/usr/bin/date +%Y%m%d`.bz2
done

/export/home/bob/bin/reaper.sh -a 60 -d /export/home/bob/backups/weekly -f "*gz"
/export/home/bob/bin/reaper.sh -a 60 -d /export/home/bob/backups/weekly -f "*bz2"
