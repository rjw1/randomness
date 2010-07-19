#!/bin/bash
# nagios plugin to check a named ipsec tunnel
while getopts "t:h" option
do
  case $option in
   t ) TUNNEL=$OPTARG ;;
   h ) HELP=1 ;;
   * ) HELP=1 ;;
  esac
done
if [[ -z $TUNNEL ]]
then
    echo "No directory to check"
    HELP=1
fi
if [ "$HELP" = "1" ]
then
  echo "check the state of a named ipsec tunnel"
  echo "-d tunnel to check"
  echo "-h this help message"
  exit 3
fi

STATUSOUTPUT=`ipsec status $TUNNEL`

if [[ $STATUSOUTPUT =~ "$TUNNEL" ]]
then
:
else
echo "$TUNNEL doesnt exist"
exit 2
fi

if  [[ $STATUSOUTPUT =~ "erouted" ]]
then
:
else
echo "not routed"
exit 2
fi

if  [[ $STATUSOUTPUT =~ "IPsec SA established" ]]
then
:
else
echo "IPsec SA not established"
exit 2
fi

if  [[ $STATUSOUTPUT =~ "ISAKMP SA established" ]]
then
:
else
echo "ISAKMP SA not established"
exit 2
fi

echo "$TUNNEL is up"

