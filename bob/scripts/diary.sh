#!/bin/bash
# script to generate my diary in html 
# to be run on nebula

# quiety update the svn directory
svn up -q /export/home/bob/web/vhosts/randomness.org.uk/diary/
#generate html from diary file 
/usr/bin/MultiMarkdown.pl /export/home/bob/web/vhosts/randomness.org.uk/diary/diary > /export/home/bob/web/vhosts/randomness.org.uk/diary/index.html
