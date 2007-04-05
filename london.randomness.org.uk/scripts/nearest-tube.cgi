#!/opt/csw/bin/perl

use strict;
use warnings;

# Hack around bug, for now.
use lib qw( /export/home/kake/tmp/Wiki-Toolkit-Plugin-Categoriser-0.05/lib );

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use Data::Dumper;
use OpenGuides;
use OpenGuides::Config;
use Wiki::Toolkit::Plugin::Locator::Grid;
use Wiki::Toolkit::Plugin::Categoriser;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $locator = Wiki::Toolkit::Plugin::Locator::Grid->new( x => "os_x", y => "os_y" );
$wiki->register_plugin( plugin => $locator );
my $categoriser = Wiki::Toolkit::Plugin::Categoriser->new; 
$wiki->register_plugin( plugin => $categoriser );
my $formatter = $wiki->formatter;

my $q = CGI->new;
print $q->header;

if ( $q->param( "origin" ) ) {
  my $origin = $q->param( "origin" );
  $origin = $formatter->node_param_to_node_name( $origin );

  my @nearby = $locator->find_within_distance( node   => $origin,
                                               metres => 1000 );
  my @stations = $wiki->list_nodes_by_metadata(
      metadata_type  => "category",
      metadata_value => "Tube",
      ignore_case    => 1,
  );
  my %stationhash = map { $_ => 1 } @stations;

  my $base_url = $config->script_url . $config->script_name . "?";
  my @results;
  foreach my $near ( @nearby ) {
    if ( $stationhash{ $near } ) {
      my $distance = $locator->distance( from_node => $origin,
                                         to_node   => $near );
      my @lines = $categoriser->categories( node => $near );
      @lines = grep { /Line$/ } @lines;
      my %uniq = map { $_ => 1 } @lines;
      @lines = keys( %uniq );
      @lines = map { s/ Line$//; $_; } @lines;
      my $url = $base_url . $formatter->node_name_to_node_param( $near );
      $near =~ s/ Station$//;
      push @results, { name => $near, distance => $distance, lines => \@lines,
                       url => $url };
    }
  }

  if ( @results == 0 ) {
    print "Nothing within 1km, sorry.\n";
  } else {
    @results = sort { $a->{distance} <=> $b->{distance} } @results;
    if ( @results > 5 ) {
      @results = @results[0..4];
    }
    my @pretty;
    foreach my $result ( @results ) {
      push @pretty, "<a href=\"" . $result->{url} . "\">" . $result->{name} . "</a> (" . $result->{distance} . "m, "
            . join( ", ", @{$result->{lines}} ) . ")";
    }
    print join( "; ", @pretty );
  }
} else {
  print "<p>No origin specified.</p>\n";
}


