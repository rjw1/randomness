#!/bin/bash
# nagios plugin to check the state of a checkout.
while getopts "d:h" option
do
  case $option in
   d ) DIRTOCHECK=$OPTARG ;;
   h ) HELP=1 ;;
   * ) HELP=1 ;;
  esac
done
if [[ -z $DIRTOCHECK ]]
then
    echo "No directory to check"
    HELP=1
fi
if [ "$HELP" = "1" ]
then
  echo "check the state of a svn checkout"
  echo "-d directory to check"
  echo "-h this help message"
  exit 3
fi



if [[ `svn st $DIRTOCHECK 2>&1`  = "" ]]
then
echo "nothing to do"
exit 0
elif svn st $DIRTOCHECK 2>&1 | grep -q "warning" 
then
echo "not a workign copy"
exit 3
elif  svn st $DIRTOCHECK | grep -q "M" 
then
echo "files modified"
exit 1
elif svn st $DIRTOCHECK | grep -q "?" 
then 
echo "files to add"
exit 1
elif svn st $DIRTOCHECK | grep -q "A"
then 
echo "files to add"
exit 1
elif svn st $DIRTOCHECK | grep -q "!"
then 
echo "files missing"
exit 1
else
echo "not and expected result"
exit 3
fi

