#!/opt/csw/bin/perl

# Still to be done:
#   - should include index pages which don't exist as nodes
#   - said pages might also use the "priority" element we don't use yet
#   - probably all a terrible kludge that can be done much more neatly

#   - some attempt at documentation or comments
#   - it would be nice to estimate change frequency. maybe unrealistic though

use strict;
use warnings;

use POSIX qw(strftime);
use CGI;
use OpenGuides::Config;
use OpenGuides::Utils;

# This script generates a Google Sitemap for a guide.

my $config = OpenGuides::Config->new( file => "/export/home/bob/web/vhosts/london.randomness.org.uk/wiki.conf" );
my $wiki = OpenGuides::Utils->make_wiki_object( config => $config );
my $formatter = $wiki->formatter;

my $timezone = strftime("%z", localtime);
$timezone =~ s/(\d\d)(\d\d)/$1:$2/;

my @nodes = $wiki->list_all_nodes;

print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
print "<urlset xmlns=\"http://www.google.com/schemas/sitemap/0.84\">\n";

foreach my $node ( sort @nodes ) {

    my %content = $wiki->retrieve_node( $node );
    my $tmp = CGI->escape($formatter->node_name_to_node_param($node));
    my $url = $config->script_url . CGI->escape($config->script_name) . "?$tmp";
    my $date = $content{last_modified};
    
    my ($day, $time) = ($date =~ /(\d+-\d+-\d+) (\d+:\d+:\d+)/);
    my $isotime = $day . "T" . $time . $timezone;

    print "<url>\n";
    print "<loc>$url</loc>\n";
    print "<lastmod>$isotime</lastmod>\n";
    print "</url>\n";

}

print "</urlset>";

