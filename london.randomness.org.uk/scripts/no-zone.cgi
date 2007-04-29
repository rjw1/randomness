#!/opt/csw/bin/perl

use strict;
use warnings;

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use OpenGuides::Config;
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

print $q->header;
my $self_url = $q->url( -relative );

my %tt_vars = (
                stylesheet => $config->stylesheet_url,
                site_name  => $config->site_name,
                script_url => $config->script_url,
                site_url   => $config->script_url . $config->script_name,
                full_cgi_url => $config->script_url . $config->script_name,
                common_categories => $config->enable_common_categories,
                common_locales => $config->enable_common_locales,
                catloc_link => $config->script_url . $config->script_name . "?id=",
              );
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH => ".:$custom_template_path:$template_path"  } );
$tt->process( "no_zone_header.tt", \%tt_vars );

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

if ( !scalar @nozones ) {
  print "<p>No Tube or rail stations without zones!  Yay!</p>\n";
} else {
  my $base_url = $config->script_url . $config->script_name . "?";
  print "<p>Tube/rail stations missing a zone:</p>\n<ul>";
  foreach my $station ( sort @nozones ) {
    my $url = $base_url . $formatter->node_name_to_node_param( $station );
    my $name = CGI->escapeHTML( $station );
    print qq( <li><a href="$url">$name</a></li>\n );
  }
  print "</ul>\n";
}

$tt->process( "find_footer.tt", \%tt_vars );
