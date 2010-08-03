#!/bin/bash
# script to tar up a specified directory
# keep only 7 days worth by default

# defaults
DAYSTOKEEP=7

while getopts "b:d:k:h" option
do
  case $option in
   b ) BACKUPDIR=$OPTARG ;;
   d ) DIRTOBACKUP=$OPTARG ;;
   h ) HELP=1 ;;
   k ) DAYSTOKEEP=$OPTARG ;;
   * ) HELP=1 ;;
  esac
done

if [[ -z $BACKUPDIR ]]
then
    echo "No backup directory set"
    HELP=1
fi

if [[ -z $DIRTOBACKUP ]]
then
    echo "No directory to backup set"
    HELP=1
fi

if [ "$HELP" = "1" ]
then
  echo "backup a directory"
  echo "-b backup directory"
  echo "-d directory to backup"
  echo "-k days to keep"
  echo "-h this help message"
  exit 0
fi
STARTEPOCH=$(date +'%s')
APPNAME=$(basename $0)
DIRNAME=$(basename $DIRTOBACKUP)
ROOTPATH=$(dirname $DIRTOBACKUP)
BACKUPFILE=${BACKUPDIR}/${DIRNAME}_backup_$(date +'%Y_%m_%d').tar.gz


if [ ! -d "$BACKUPDIR" ]; then
  echo "$APPNAME: The backup destination directory '$BACKUPDIR' doesn't exist..."
  exit 1
fi

if [ ! -d "$DIRTOBACKUP" ]; then
  echo "$APPNAME: The backup destination directory '$DIRTOBACKUP' doesn't exist..."
  exit 1
fi

STARTCLEAN=$(date +'%s')
find $BACKUPDIR -name "*_backup_*" -mtime +${DAYSTOKEEP} -exec rm {} \;
STOPCLEAN=$(date +'%s')
STARTBACKUP=$(date +'%s')
/bin/tar -zcf $BACKUPFILE -C $ROOTPATH $DIRNAME
STOPBACKUP=$(date +'%s')
FINISHEPOCH=$(date +'%s')
CLEANTIME=$(expr  $STOPCLEAN  - $STARTCLEAN)
TOTALTIME=$(expr $FINISHEPOCH - $STARTEPOCH)
BACKUPTIME=$(expr $STOPBACKUP - $STARTBACKUP)

logger -i -p local0.notice -t $APPNAME "Backup of $DIRNAME completed: B:$BACKUPTIME C:$CLEANTIME T:$TOTALTIME seconds"

