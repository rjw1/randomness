#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "lib";

use Geo::GoogleEarth::Document;
use OpenGuides;
use OpenGuides::Config;
use RGL::Addons;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );
my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my @nodes = RGL::Addons->get_nodes_with_geodata( wiki => $wiki,
                                                 config => $config,
                                                 return_latlong => 1 );

my $doc = Geo::GoogleEarth::Document->new;

my $base_url = $config->script_url . $config->script_name;
foreach my $node ( @nodes ) {
    my $url = $base_url . "?"
              . $formatter->node_name_to_node_param( $node->{name} );
    my $desc = "<a href=\"$url\">RGL entry</a>";
    $doc->Placemark(
                     name => $node->{name},
                     lat  => $node->{lat},
                     lon  => $node->{long},
                     description => $desc,
                   );
}

print $doc->render;
