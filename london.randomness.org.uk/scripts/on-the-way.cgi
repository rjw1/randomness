#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "lib";

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use Data::Dumper;
use Geo::HelmertTransform;
use OpenGuides;
use OpenGuides::Config;
use RGL::Addons;
use Template;
use Wiki::Toolkit::Plugin::Locator::Grid;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $locator = Wiki::Toolkit::Plugin::Locator::Grid->new( x => "os_x",
                                                         y => "os_y" );
$wiki->register_plugin( plugin => $locator );
my $formatter = $wiki->formatter;

my $fudge = 300;

my $q = CGI->new;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );
$tt_vars{self_url} = $q->url( -relative );

$tt_vars{os_x_origin_box} = $q->textfield( -name =>"x1",
                                           -size => 6, -maxlength => 6 );
$tt_vars{os_y_origin_box} = $q->textfield( -name =>"y1",
                                           -size => 6, -maxlength => 6 );
$tt_vars{os_x_destin_box} = $q->textfield( -name =>"x2",
                                           -size => 6, -maxlength => 6 );
$tt_vars{os_y_destin_box} = $q->textfield( -name =>"y2",
                                           -size => 6, -maxlength => 6 );

my @all_nodes = get_nodes_with_geodata();
my %choices = map { $_ => $_ } @all_nodes;
$tt_vars{origin_list} = $q->popup_menu( -name   => "origin",
                                        -values => [ "", sort keys %choices ],
                                        -labels => { "" => " -- choose -- ",
                                                     %choices },
                                      );
$tt_vars{destin_list} = $q->popup_menu( -name   => "dest",
                                        -values => [ "", sort keys %choices ],
                                        -labels => { "" => " -- choose -- ",
                                                     %choices },
                                      );
my @buttons = $q->radio_group( -name   => "choose_how",
                               -values => [ "os", "name" ],
                               -labels => { os => "", name => "" } );
$tt_vars{choose_how_buttons} = { os => $buttons[0], name => $buttons[1] };

if ( $q->param( "do_search" ) ) {
  do_search();
}

# Make sure the maps work.
$tt_vars{enable_gmaps} = 1;
$tt_vars{display_google_maps} = 1;

# Do the template stuff.
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );
%tt_vars = (
             %tt_vars,
             addon_title => "Things on the way to other things",
           );

print $q->header;
$tt->process( "on_the_way.tt", \%tt_vars ) || die $tt->error;

sub get_nodes_with_geodata {
  my $dbh = $wiki->store->dbh;
  my $sql = "
    SELECT node.name
    FROM node
    INNER JOIN metadata as mx
      ON ( node.id=mx.node_id
           AND node.version=mx.version
           AND lower(mx.metadata_type)='os_x' )
    INNER JOIN metadata as my
      ON ( node.id=my.node_id
           AND node.version=my.version
           AND lower(my.metadata_type)='os_y' )
    INNER JOIN metadata as mlat
      ON ( node.id=mlat.node_id
           AND node.version=mlat.version
           AND lower(mlat.metadata_type)='latitude' )
    INNER JOIN metadata as mlong
      ON ( node.id=mlong.node_id
           AND node.version=mlong.version
           AND lower(mlong.metadata_type)='longitude' )
    ORDER BY node.name";

  my $sth = $dbh->prepare( $sql );
  $sth->execute or die $dbh->errstr;

  my @nodes;
  while ( my ( $name ) = $sth->fetchrow_array ) {
    push @nodes, $name;
  }
  return @nodes;
}

sub do_search {
  my $x1 = $q->param( "x1" ) || "";
  my $y1 = $q->param( "y1" ) || "";
  my $x2 = $q->param( "x2" ) || "";
  my $y2 = $q->param( "y2" ) || "";
  my $choose_how = $q->param( "choose_how" ) || "os";
  my $origin = $q->param( "origin" ) || "";
  my $dest = $q->param( "dest" ) || "";

  if ( $choose_how eq "name" ) {
    if ( !$origin || !$dest ) {
      $tt_vars{message} = "Must supply both origin and destination.";
      return;
    }
  } elsif ( !$x1 || !$y1 || !$x2 || !$y2 ) {
    $tt_vars{message} = "Must supply x and y for both origin and destination.";
    return;
  }

  if ( $choose_how eq "name" ) {
    ( $x1, $y1 ) = $locator->coordinates( node => $origin );
    ( $x2, $y2 ) = $locator->coordinates( node => $dest );
  }

  # First get points within bounding box.
  my $dbh = $wiki->store->dbh;
  my $sql = "
    SELECT node.name, mx.metadata_value as x, my.metadata_value as y,
           mlat.metadata_value as lat, mlong.metadata_value as long
    FROM node
      INNER JOIN metadata as mx
        ON ( node.id=mx.node_id
             AND node.version=mx.version
             AND lower(mx.metadata_type)='os_x'
             AND mx.metadata_value::integer >= ?
             AND mx.metadata_value::integer <= ? )
      INNER JOIN metadata as my
        ON ( node.id=my.node_id
             AND node.version=my.version
             AND lower(my.metadata_type)='os_y'
             AND my.metadata_value::integer >= ?
             AND my.metadata_value::integer <= ? )
      INNER JOIN metadata as mlat
        ON ( node.id=mlat.node_id
             AND node.version=mlat.version
             AND lower(mlat.metadata_type)='latitude' )
      INNER JOIN metadata as mlong
        ON ( node.id=mlong.node_id
             AND node.version=mlong.version
             AND lower(mlong.metadata_type)='longitude' )
    ORDER BY node.name";

  my $sth = $dbh->prepare( $sql );

  my $lbx = $x1 < $x2 ? $x1 : $x2;
  my $lby = $y1 < $y2 ? $y1 : $y2;
  my $ubx = $x1 > $x2 ? $x1 : $x2;
  my $uby = $y1 > $y2 ? $y1 : $y2;

  $sth->execute( $lbx - $fudge, $ubx + $fudge, $lby - $fudge, $uby + $fudge )
      or die $dbh->errstr;

  # If x1=x2 or y1=y2 then the bounding box is exactly what we want.
  my $slope;
  if ( $x1 == $x2 ) {
    $slope = 0;
  } else {
    $slope = ( $y2 - $y1 ) / ( $x2 - $x1 );
  }

  my $airy  = Geo::HelmertTransform::Datum->new( Name => "Airy1830" );
  my $wgs84 = Geo::HelmertTransform::Datum->new( Name => "WGS84" );

  my @candidates;
  while ( my ( $name, $x, $y, $lat, $long ) = $sth->fetchrow_array ) {
    my $vertdist = abs( $y1 + $slope*( $x - $x1 ) - $y );
    if ( $vertdist > $fudge ) {
      next;
    }
    my $param = $formatter->node_name_to_node_param( $name );
    ( $lat, $long ) =
       Geo::HelmertTransform::convert_datum( $airy, $wgs84, $lat, $long, 0 );
    my $endpoint = 0;
    if ( ( $origin && $name eq $origin  ) || ( $dest && $name eq $dest ) ) {
      $endpoint = 1;
    }
    push @candidates, { name => $name, x => $x, y => $y, lat => $lat,
                        long => $long, param => $param, endpoint => $endpoint };
  }

  $tt_vars{nodes} = \@candidates;

  if ( scalar @candidates ) {
    %tt_vars = (
                 %tt_vars,
                 x1       => $x1,
                 y1       => $y1,
                 x2       => $x2,
                 y2       => $y2,
                 long     => $q->param( "long" ) || $config->centre_long,
                 lat      => $q->param( "lat" ) || $config->centre_lat,
                 zoom     => $q->param( "zoom" )
                                 || $config->default_gmaps_zoom,
                 map_type => $q->param( "map_type" ) || "",
                 base_url => $config->script_url . $config->script_name,
               );
  }
}


