#!/usr/bin/bash
# script to generate rgl import data files
# take the first argument as the name of hte fiel to write to.
FILENAME=$1
echo "name?"
read NAME
echo "postcode?"
read POSTCODE
echo "maplink?"
read MAPLINK
echo "address?"
read ADDRESS
echo "phone?"
read PHONE
echo "opening?"
read OPENING
echo "locales?"
read LOCALES
echo "categories?"
read CATEGORIES
echo "summary?"
read SUMMARY
echo "extra content?"
read EC
echo "website?"
read WEBSITE
echo "image?"
read IMAGE
echo "image owner?"
read OWNER
echo "licence url?"
read LICENCE
echo "image page?"
read IMAGEPAGE

echo "---" >> $FILENAME
echo "pagename: $NAME, $POSTCODE" >> $FILENAME
echo "postcode: $POSTCODE" >> $FILENAME
echo "map_link: $MAPLINK" >> $FILENAME
echo "address: $ADDRESS" >> $FILENAME
echo "phone: $PHONE" >> $FILENAME
echo "locales: $LOCALES" >> $FILENAME
echo "categories: $CATEGORIES" >> $FILENAME
echo "summary: $SUMMARY" >> $FILENAME
echo "website: $WEBSITE" >> $FILENAME
echo "node_image: $IMAGE" >> $FILENAME
echo "node_image_copyright: $OWNER" >> $FILENAME
echo "node_image_licence: $LICENCE" >> $FILENAME
echo "node_image_url: $IMAGEPAGE" >> $FILENAME
echo "hours_text: $OPENING" >> $FILENAME
echo "extra_content: \"$EC\"" >> $FILENAME
