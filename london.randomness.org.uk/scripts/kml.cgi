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

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );
my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH => ".:$custom_template_path:$template_path"  } );

my $q = CGI->new;

my $locale = $q->param( "locale" );
my $category = $q->param( "category" );

if ( !$locale && !$category ) {
  my %tt_vars = (
                  message => "Must supply either a locale or a category "
                             . "(or both).",
                  return_url => $q->self_url,
                );
  print $q->header;
  $tt->process( "error.tt", \%tt_vars );
  exit 0;
}

my %args;
if ( $locale ) {
  $args{locale} = $locale;
}
if ( $category ) {
  $args{category} = $category;
}

my @nodes = RGL::Addons->get_nodes_with_geodata( wiki => $wiki,
                                                 config => $config,
                                                 return_latlong => 1,
                                                 %args,
                                               );

my @points;

my $base_url = $config->script_url . $config->script_name;
foreach my $node ( @nodes ) {
    my %data = %$node;
    my $param = $formatter->node_name_to_node_param( $data{name} );
    $data{url} = $base_url . "?" . $param;
    push @points, \%data;
}

my %tt_vars = ( points => \@points );

print $q->header( "application/vnd.google-earth.kml+xml" );
#print $q->header( "application/vnd.google-earth.kml" );
$tt->process( "kml.tt", \%tt_vars );
