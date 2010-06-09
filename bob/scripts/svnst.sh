#!/bin/bash
if svn st $1 2>&1 | grep "warning" > /dev/null
then
echo "not a workign copy"
elif  svn st $1 | grep "M" > /dev/null
then
echo "files modified"
elif svn st $1 | grep "?" > /dev/null 
then 
echo "files to add"
elif svn st $1 | grep "A" > /dev/null 
then 
echo "files to add"
elif svn st $1 | grep "!" > /dev/null 
then 
echo "files missing"
elif [[svn st $1  = ""]]
then
echo "nothing to do"
else
beeep
fi

