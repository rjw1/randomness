#!/bin/bash
# script to wrap flickr_upload from Flickr::Upload on CPAN
echo File to be uploaded $1
eog $1
echo "wanna upload?(y/n)"
read upload
if [[ "$upload" == "n" ]]
then
	exit 1
fi
echo Title?
read title
echo description?
read desc
echo tags?
read tags

/usr/bin/flickr_upload --title "$title" --description "$desc" --tag "$tags" $1
echo $1 processed
