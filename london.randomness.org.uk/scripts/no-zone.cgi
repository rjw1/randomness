#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "lib";

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use OpenGuides::Config;
use RGL::Addons;
use Template;
use Wiki::Toolkit::Plugin::Categoriser;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $categoriser = Wiki::Toolkit::Plugin::Categoriser->new;
$wiki->register_plugin( plugin => $categoriser );
my $formatter = $wiki->formatter;

my $q = CGI->new;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

# Get stations.
my @tubes = $wiki->list_nodes_by_metadata(
    metadata_type => "category",
    metadata_value => "tube",
    ignore_case => 1,
);
my @rails = $wiki->list_nodes_by_metadata(
    metadata_type => "category",
    metadata_value => "rail",
    ignore_case => 1,
);
my @stations = ( @tubes, @rails );

# Strip out the ones that are categories (they're lines).
my @cats = $wiki->list_nodes_by_metadata(
    metadata_type => "category",
    metadata_value => "category",
    ignore_case => 1,
);
my %stationhash = map { $_ => 1 } @stations;
my %cathash = map { $_ => 1 } @cats;
foreach my $key ( @stations ) {
  if ( $cathash{$key} ) {
    delete $stationhash{$key};
  }
}
@stations = keys %stationhash;

my @nozones;
foreach my $station ( sort @stations ) {
  my @cats = $categoriser->categories( node => $station );
  my @zones = grep { /Zone.*Stations/ } @cats;
#  print "$station has zones: " . join( ", ", @zones ) . "\n";
  if ( !scalar @zones ) {
    push @nozones, $station;
  }
}

my @lacking;
if ( scalar @nozones ) {
  my $base_url = $config->script_url . $config->script_name . "?";
  foreach my $station ( sort @nozones ) {
    my $url = $base_url . $formatter->node_name_to_node_param( $station );
    my $name = CGI->escapeHTML( $station );
    push @lacking, { name => $name, url => $url };
  }
}

%tt_vars = (
             %tt_vars,
             addon_title => "Stations with no zone",
             lacking     => \@lacking,
           );

# Do the template stuff.
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH => ".:$custom_template_path:$template_path"  } );

print $q->header;
$tt->process( "no_zone.tt", \%tt_vars );
