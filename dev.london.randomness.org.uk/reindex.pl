#!/usr/bin/perl

use strict;
use warnings;
use lib qw( /export/home/rgl/web/vhosts/london.randomness.org.uk/scripts/lib/ );
use lib qw( /export/home/rgl/perl5/lib/perl5 );


use OpenGuides::Config;
use OpenGuides::Utils;

# This is a simple script to reindex every node in the wiki, useful if
# your indexes got screwed up or you're swapping to a different searcher.

my $config = OpenGuides::Config->new( file => "wiki.conf" );
my $wiki = OpenGuides::Utils->make_wiki_object( config => $config );

my @nodes = $wiki->list_all_nodes;
foreach my $node ( sort @nodes ) {
    my $content = $wiki->retrieve_node( $node );
    $wiki->search_obj->index_node( $node, $content );
    print "Reindexed $node\n";
}
