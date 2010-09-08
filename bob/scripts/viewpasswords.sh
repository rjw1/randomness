#!/bin/bash
# script to view an encrypted passowrd file

echo "checking we are up to date"
svn st
echo -n "enter the password:"
read -s password
echo ""
openssl aes-256-cbc -d -a -in passwords.enc -k $password |less


