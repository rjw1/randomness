#!/usr/bin/bash
# script to do a test cpan modules against the perls I have installed in the my homedir

# accept defaut modules for Module::Autoinstall modules.
export PERL_AUTOINSTALL='--defaultdeps'

#ensure the sun compiler is my path before anything else
PATH=/opt/SUNWspro/bin:$PATH
#
# remove search.cpan stuff for input. has the side effect that just a modulename will also work. 
# normal input should be a download link for the module.
MODULE=`echo $1 | sed -e 's#http://search.cpan.org/CPAN/authors/id/##'`
echo $MODULE
# test against perl 5.8.8
# remove the old tree
rm -rf /export/home/bob/cpantesting/perl-5.8.8
# untar to get a new tree
gtar -zxf /export/home/bob/cpantesting/perl-5.8.8.tar.gz -C /export/home/bob/cpantesting/
/export/home/bob/cpantesting/perl-5.8.8/bin/cpan $MODULE
# test against perl 5.10.0
rm -rf /export/home/bob/cpantesting/perl-5.10.0
gtar -zxf /export/home/bob/cpantesting/perl-5.10.0.tar.gz -C /export/home/bob/cpantesting/
/export/home/bob/cpantesting/perl-5.10.0/bin/cpan $MODULE
echo "Finished $MODULE"
