#!/bin/bash
# script to wrap flickr_upload from Flickr::Upload on CPAN
echo File to be uploaded: $1
feh -. $1
echo "Upload? (y/n)"
read upload
if [[ "$upload" == "n" ]]
then
	exit 1
fi
echo Title?
read title
echo Description?
read desc
echo Tags?
read tags

flickr_upload --title "$title" --description "$desc" --tag "$tags" $1
notify-send -t 2000 $1 uploaded
echo $1 processed.
