#!/usr/local/bin/bash
# Mp3Maker 24032001 bob walker randomness ltd
# Script to rip, encode, and rename mp3s
# Script uses cdparanoia, bladeenc, mp3cddb and mp3cdbtag
# Developed on OpenBSD 2.8 



# check the user gave the right variables
# these are the number of tracks on the cd 
# and the name of the cd for the directory to put it in.


if [ $# != 2 ]
then
echo ripper.sh tracks directory 
exit 9
fi

# set some things up
# like dir to work in
TRACK=1
mkdir /mp3/mp3/$2
cd /mp3/mp3/$2 

# first loop to rip wav files from cd 

while [ $TRACK -le  $1 ]
 do
/usr/local/bin/cdparanoia -q  $TRACK track$TRACK.wav 
TRACK=$[ $TRACK + 1 ]
done
TRACK=1

# loop to encode wav files to mp3 and then remove wav files

while [ $TRACK -le  $1 ]
 do
/usr/local/bin/bladeenc -q -quiet -progress=0  track$TRACK.wav track$TRACK.mp3
rm track$TRACK.wav
TRACK=$[ $TRACK + 1 ]
done

# get cddb data

/usr/local/bin/mp3cddb *.mp3

# tag up and rename mp3s 

/usr/local/bin/mp3cddbtag cddbinfo.txt
exit 0 
