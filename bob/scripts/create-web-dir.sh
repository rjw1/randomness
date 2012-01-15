#!/bin/bash
#script to create dirs for a website. 

while getopts "s:h" option
do
  case $option in
   s ) SITE=$OPTARG ;;
   h ) HELP=1 ;;
   * ) HELP=1 ;;
  esac
done


if [[ -z $SITE ]]
then
    echo "no site set"
    HELP=1
fi
if [ "$HELP" = "1" ]
then
  echo "create website directories"
  echo "-s site name"
  echo "-h this help text"
  exit 0
fi

mkdir -p ~/web/vhosts/$SITE
mkdir -p ~/web/logs/$SITE

