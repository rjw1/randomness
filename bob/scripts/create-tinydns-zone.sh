#!/bin/bash
echo "Z$1:nimbus.geekcloud.com.:domains.randomness.org.uk.::21600:3600:604800:21600:21600" >> /service/tinydns/master/$1

echo "&$1::nimbus.geekloud.com.:21600" >> /service/tinydns/master/$1 
echo "&$1::gertie.vm.bytemark.co.uk.:21600" >> /service/tinydns/master/$1 
echo "+$1:46.37.32.131:21600" >> /service/tinydns/master/$1 
echo "@$1::nimbus.geekcloud.com.:5:21600" >> /service/tinydns/master/$1 
echo "+www.$1:46.37.32.131:21600" >> /service/tinydns/master/$1 

