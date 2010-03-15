#!/bin/bash
# script to check the health of services being load balanced by ipvs
# intended to be run as a nagios check under nrpe. needs sudo access

# options to set port and ip
while getopts "i:f:p:t:r:h" option

do
  case $option in
    p ) PORT=$OPTARG   ;;
    i ) IP=$OPTARG     ;;
    t)  ETOTAL=$OPTARG ;;
    r)  REALIPSTRING=$OPTARG ;;
    f)  FALLBACKIPSTRING=$OPTARG ;;
    h ) HELP=1 ;;
    * ) HELP=1 ;;
  esac
done


# make sure we have ip and port set
if [[ -z $PORT ]]
then
echo "no port"
HELP=1
fi

if [[ -z $IP ]]
then
echo "no IP"
HELP=1
fi

# help output
if [ "$HELP" = "1" ]
then
echo "Check ipvs status"
echo "-i IP address of virtual server. REQUIRED"
echo "-p port. REQUIRED"
echo "-t expected total of real servers. OPTIONAL"
echo "-r string to match real servers. OPTIONAL. DEFAULT=172"
echo "-f string to match fallback server. OPTIONAL. DEFAULT=127"

echo "-h this message"
exit 3
fi
# check /sbin/ipvsadm exists
if [ ! -x /sbin/ipvsadm ]
then
echo "ipvsadm not on this machine!"
exit 3
fi
#check that the script is being run by root
if [ "$UID" != "0" ]
then
echo "Needs to be run as root or under sudo"
exit 3
fi
# set REALIPSTRING if none is given on the command line
if [[ -z $REALIPSTRING ]]
then
REALIPSTRING="172"
fi
# ser FALLBACKIPSTRING if none is given on the command line
if [[ -z $FALLBACKIPSTRING ]]
then
FALLBACKIPSTRING="127"
fi

# find real servers with a weight of 0. 
OUT=`/sbin/ipvsadm -L -n -t $IP:$PORT --sort | awk '{print $2" "$4}'| grep ^$REALIPSTRING |awk '{print $2}' | grep -c 0`
# find real servers with a weight of 1
IN=`/sbin/ipvsadm -L -n -t $IP:$PORT --sort | awk '{print $2" "$4}'| grep ^$REALIPSTRING |awk '{print $2}' | grep -c 1`
# calculate the total number of servers. 
TOTAL=`/sbin/ipvsadm -L -n -t $IP:$PORT --sort | awk '{print $2}'| grep -c ^$REALIPSTRING `
# see if we have fallen back to localhost
FALLBACK=`/sbin/ipvsadm -L -n -t $IP:$PORT --sort | awk '{print $2" "$3}' |grep Local |grep -c ^$FALLBACKIPSTRING`


# Check if we have fallen back to localhost. Return critical if we have
if [ "$FALLBACK" != "0" ]
then 
echo "CRITICAL - Using Fallback - TOTAL: $TOTAL ACTIVE: $IN INACTIVE: $OUT"
exit 2
fi

# Check if there are no real servers. Return critical if there none
if [ "$IN" = "0" ]
then
echo "CRITICAL - No active IPs in Pool - TOTAL: $TOTAL ACTIVE: $IN INACTIVE: $OUT"
exit 2
fi

# Check if there are any real servers with a weight of 0. Warn if there is. 
if [ "$OUT" != "0" ]
then
echo "WARNING - Some IPs no longer active - TOTAL: $TOTAL ACTIVE: $IN INACTIVE: $OUT"
exit 1
fi
# Check that the total is 0. If it is 0 this means the service hasnt been set up. 
if [ "$TOTAL" = "0" ]
then
echo "CRITICAL - This service is not present or the check is not running under sudo"
exit 2
fi
# check if  ETOTAL has been set.
if [[ ! -z $ETOTAL ]]
then
# If it has check if it doesnt equal are calculated total. If it doesnt return critical
	if [ "$TOTAL" != "$ETOTAL" ]
	then
	echo "CRITICAL - Total number of real servers does not match expected total. TOTAL: $TOTAL Expected Total: $ETOTAL"
	exit 2
	fi
fi

# Everything should be okay if its got this far so return ok. 


echo "OK - TOTAL: $TOTAL ACTIVE: $IN INACTIVE: $OUT"
