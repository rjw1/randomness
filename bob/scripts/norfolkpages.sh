#!/usr/local/bin/bash
# script to take norfolks db then turn it inot a nice set of files for webpages to read in
# bob walker Randomness Ltd 14062002
/export/home/norfolk/scripts/dump_db /export/home/norfolk/norfolk-is | sort -d > /export/home/bob/web/hosts/randomness.org.uk/norfolk/sorted.norfolk
# dump the database and sort it.
grep -v '^[a-z0-9]' /export/home/bob/web/hosts/randomness.org.uk/norfolk/sorted.norfolk >/export/home/bob/web/hosts/randomness.org.uk/norfolk/randomthings.norfolk.pre
sed -e 's/=>/is/' -e 's/<reply>/\&lt;reply\&gt;/'  -e 's/<action>/\&lt;action\&gt;/' -e 's/\(http:\/\/[a-z\.0-9\/A-Z~_+-\&\?]*\)/<a href="\1">\1<\/a> /g' -e 's/$/<br>/' /export/home/bob/web/hosts/randomness.org.uk/norfolk/randomthings.norfolk.pre > /export/home/bob/web/hosts/randomness.org.uk/norfolk/randomthings.norfolk
rm /export/home/bob/web/hosts/randomness.org.uk/norfolk/randomthings.norfolk.pre

for ALPHA in `ls /usr/share/lib/terminfo`
do
GERP="^$ALPHA"
#echo $GERP
grep $GERP /export/home/bob/web/hosts/randomness.org.uk/norfolk/sorted.norfolk > /export/home/bob/web/hosts/randomness.org.uk/norfolk/$ALPHA.norfolk.pre
sed -e 's/@/editATfuckoffspammers/g' -e 's/=>/is/' -e 's/<reply>/\&lt;reply\&gt;/'  -e 's/<action>/\&lt;action\&gt;/' -e 's/\(http:\/\/[a-z\.0-9\/A-Z~_+-\&\?=%]*\)/<a href="\1">\1<\/a> /g' -e 's/$/<br>/' /export/home/bob/web/hosts/randomness.org.uk/norfolk/$ALPHA.norfolk.pre > /export/home/bob/web/hosts/randomness.org.uk/norfolk/$ALPHA.norfolk
rm /export/home/bob/web/hosts/randomness.org.uk/norfolk/$ALPHA.norfolk.pre
done


