#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "/export/home/bob/web/vhosts/london.randomness.org.uk/scripts/lib";

use OpenGuides;
use OpenGuides::Config;
use RGL::Addons;
use Template;
use Wiki::Toolkit::Plugin::Categoriser;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );
my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my $categoriser = Wiki::Toolkit::Plugin::Categoriser->new;
$wiki->register_plugin( plugin => $categoriser );

my @nodes = RGL::Addons->get_nodes_with_geodata( wiki => $wiki,
                                                 config => $config,
                                                 return_latlong => 1 );

my @points;

my $base_url = $config->script_url . $config->script_name;
foreach my $node ( @nodes ) {
    my %data = %$node;
    my $name = $data{name};
    my $param = $formatter->node_name_to_node_param( $name );
    $data{url} = $base_url . "?" . $param;
    my %cathash = map { $_ => 1 } $categoriser->categories( node => $name );
    $data{categories} = [ sort keys %cathash ];
    push @points, \%data;
}

my %tt_vars = ( points => \@points );

my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH => ".:$custom_template_path:$template_path"  } );
$tt->process( "kml.tt", \%tt_vars );
