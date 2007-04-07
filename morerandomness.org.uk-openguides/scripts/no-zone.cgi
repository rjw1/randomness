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

# Get Tube stations.
my @tubes = $wiki->list_nodes_by_metadata(
    metadata_type => "category",
    metadata_value => "tube",
    ignore_case => 1,
);

# Strip out the ones that are categories (they're lines).
my @cats = $wiki->list_nodes_by_metadata(
    metadata_type => "category",
    metadata_value => "category",
    ignore_case => 1,
);
my %tubehash = map { $_ => 1 } @tubes;
my %cathash = map { $_ => 1 } @cats;
foreach my $key ( @tubes ) {
  if ( $cathash{$key} ) {
    delete $tubehash{$key};
  }
}
@tubes = keys %tubehash;

my @nozones;
foreach my $tube ( sort @tubes ) {
  my @cats = $categoriser->categories( node => $tube );
  my @zones = grep { /Zone.*Stations/ } @cats;
#  print "$tube has zones: " . join( ", ", @zones ) . "\n";
  if ( !scalar @zones ) {
    push @nozones, $tube;
  }
}

if ( !scalar @nozones ) {
  print "<p>No Tube stations without zones!  Yay!</p>\n";
} else {
  my $base_url = $config->script_url . $config->script_name . "?";
  print "<p>Tube stations missing a zone:</p>\n<ul>";
  foreach my $tube ( sort @nozones ) {
    my $url = $base_url . $formatter->node_name_to_node_param( $tube );
    my $name = CGI->escapeHTML( $tube );
    print qq( <li><a href="$url">$name</a></li>\n );
  }
  print "</ul>\n";
}

$tt->process( "find_footer.tt", \%tt_vars );
