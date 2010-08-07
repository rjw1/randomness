#!/bin/bash
# script to reap arbitary files over an arbitary age

while getopts "d:a:f:h" option
do
  case $option in
   d ) DIRTOREAP=$OPTARG ;;
   a ) FILEAGE=$OPTARG ;;
   f ) FILEGLOB=$OPTARG ;;
   h ) HELP=1 ;;
   * ) HELP=1 ;;
  esac
done

if [[ -z $DIRTOREAP ]]
then
    echo "No directory to reap set"
    HELP=1
fi
if [[ -z $FILEAGE ]]
then
    echo "No fileage set"
    HELP=1
fi

if [[ -z $FILEGLOB ]]
then
    echo "No fileglob set "
    HELP=1
fi
if [ "$HELP" = "1" ]
then
  echo "reap files from a directory older than a set number of days"
  echo "-d directory to reap"
  echo "-a age of files to reap"
  echo "-f a glob of the name to reap. must be quoted"
  echo "-h this help message"
  exit 0
fi
STARTEPOCH=$(date +'%s')
APPNAME=$(basename $0)

if [ ! -d "$DIRTOREAP" ]; then
  echo "$APPNAME: The backup destination directory '$DIRTOREAP' doesn't exist..."
  exit 1
fi

  STARTCLEAN=$(date +'%s')
find $DIRTOREAP -name "$FILEGLOB" -mtime +$FILEAGE -exec rm {} \;

  STOPCLEAN=$(date +'%s')

FINISHEPOCH=$(date +'%s')
CLEANTIME=$(expr  $STOPCLEAN    - $STARTCLEAN)

TOTALTIME=$(expr $FINISHEPOCH - $STARTEPOCH)

logger -i -p local0.notice -t $APPNAME "reap of $DIRTOREAP completed: T:$TOTALTIME seconds"

