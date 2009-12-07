#!/usr/bin/bash
# script to do a test cpan modules against the perls I have installed in the my homedir

# accept defaut modules for Module::Autoinstall modules.
export PERL_AUTOINSTALL='--defaultdeps'
export PERL_MM_USE_DEFAULT=1
export AUTOMATED_TESTING=1
export TMPDIR=$HOME/cpantesting/tmp/
# start date
STARTDATE=`date`
#ensure the sun compiler is my path before anything else
PATH=/opt/SUNWspro/bin:$PATH
#
# remove search.cpan stuff for input. has the side effect that just a modulename will also work. 
# normal input should be a download link for the module.
MODULE=`echo $1 | sed -e 's#http://search.cpan.org/CPAN/authors/id/##'`
if [ -n "$MODULE" ]
then
 
echo "Started $MODULE $STARTDATE"
echo "Started $MODULE $STARTDATE" >> $HOME/cpantesting/history/tested
# Perl versions available
PERLVERS="5.10.0 5.10.1 5.8.9"


#Do testing

for PERL in $PERLVERS
do
echo $PERL
# remove current tree if it exists
rm -rf $HOME/cpantesting/perl-$PERL
# untar the clean tree
gtar -zxf $HOME/cpantesting/perl-${PERL}.tar.gz -C $HOME/cpantesting/
# actually install the module.
$HOME/cpantesting/perl-${PERL}/bin/cpan $MODULE
done

FINISHDATE=`date`
echo "Finished $MODULE $FINISHDATE"
echo "Finished $MODULE $FINISHDATE" >> $HOME/cpantesting/history/tested
else
echo "no module $1"
echo "no module $1" >> $HOME/cpantesting/history/tested
fi

