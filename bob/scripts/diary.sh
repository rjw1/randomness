#!/bin/bash
# script to generate my diary in html 
# to be run on nmbus
export MODULEBUILDRC="/export/home/bob/perl5/.modulebuildrc"
export PERL_MM_OPT="INSTALL_BASE=/export/home/bob/perl5"
export PERL5LIB="/export/home/bob/perl5/lib/perl5/i386-pc-solaris2.11-thread-multi:/export/home/bob/perl5/lib/perl5"
export PATH="/export/home/bob/perl5/bin:$PATH"


# quiety update the svn directory
svn up -q /export/home/bob/web/vhosts/randomness.org.uk/diary/
#generate html from diary file 
MultiMarkdown.pl /export/home/bob/web/vhosts/randomness.org.uk/diary/diary > /export/home/bob/web/vhosts/randomness.org.uk/diary/index.html
