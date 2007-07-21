#!/usr/bin/bash
# script to update my whitelists.
echo "$1" >> ~/.whitelist
echo "whitelist_from $1" >> ~/.spamassassin/user_prefs
