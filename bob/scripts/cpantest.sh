#!/usr/bin/bash
MODULE=`echo $1 | sed -e 's#http://search.cpan.org/CPAN/authors/id/##'`
echo $MODULE
rm -rf /export/home/bob/cpantesting/perl-5.8.8
gtar -zxf /export/home/bob/cpantesting/perl-5.8.8.tar.gz -C /export/home/bob/cpantesting/
/export/home/bob/cpantesting/perl-5.8.8/bin/cpan $MODULE
