#!/bin/bash
# script to edit the enctypted password file
tmpfile=$$
echo "checking were up to date"
svn st 
echo -n "enter the password:"
read -s password
echo ""
openssl aes-256-cbc -d -a -in passwords.enc -k $password -out $tmpfile.decrypt
cp $tmpfile.decrypt $tmpfile.decrypt.orig
$EDITOR $tmpfile.decrypt
if diff -qs $tmpfile.decrypt $tmpfile.decrypt.orig
then

echo "no changes detected"
else
openssl aes-256-cbc -a -salt -in $tmpfile.decrypt -out passwords.enc -k $password
svn ci passwords.enc
fi

rm $tmpfile.de* 
