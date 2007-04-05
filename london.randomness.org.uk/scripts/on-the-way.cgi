#!/opt/csw/bin/perl

use strict;
use warnings;

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use Data::Dumper;
use Geo::HelmertTransform;
use OpenGuides;
use OpenGuides::Config;
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

my $fudge = 200;

my $q = CGI->new;

my $raw = $q->param( "raw" );

print $q->header unless $raw;
my $self_url = $q->url( -relative );

my %tt_vars = (
                stylesheet    => $config->stylesheet_url,
                gmaps_api_key => $config->gmaps_api_key,
                site_name     => $config->site_name,
                home_link     => $config->script_url . $config->script_name,
              );
my $tt = Template->new( { INCLUDE_PATH => "." } );
$tt->process( "on-the-way-header.tt", \%tt_vars ) unless $raw;;

my $x1 = $q->param( "x1" ) || "";
my $y1 = $q->param( "y1" ) || "";
my $x2 = $q->param( "x2" ) || "";
my $y2 = $q->param( "y2" ) || "";
my $origin = $q->param( "origin" ) || "";
my $dest = $q->param( "dest" ) || "";
my $choose_how = $q->param( "choose_how" ) || "os";

print_form() unless $raw;

if ( $q->param( "do_search" ) ) {
  do_search();
}

print <<EOHTML;
</body>
</html>
EOHTML

sub print_form {
  my $origin_boxes = <<EOHTML;
    OS X <input type="text" size="6" maxlength="6" name="x1" value="$x1" />
    OS Y <input type="text" size="6" maxlength="6" name="y1" value="$y1" />
EOHTML
  my $dest_boxes = <<EOHTML;
    OS X <input type="text" size="6" maxlength="6" name="x2" value="$x2" />
    OS Y <input type="text" size="6" maxlength="6" name="y2" value="$y2" />
EOHTML
  my @all_nodes = get_nodes_with_geodata();
  my %choices = map { $_ => $_ } @all_nodes;
  my $origin_list = $q->popup_menu( -name   => "origin",
                                    -values => [ "", sort keys %choices ],
                                    -labels => { "" => " -- choose -- ",
                                                 %choices },
                                  );
  my $dest_list = $q->popup_menu(   -name   => "dest",
                                    -values => [ "", sort keys %choices ],
                                    -labels => { "" => " -- choose -- ",
                                                 %choices },
                                  );
  my $choose_os = '<input type="radio" name="choose_how" value="os" '
                  . ( $choose_how eq "os" ? "checked=\"1\" " : "" ) . '/>';
  my $choose_name = '<input type="radio" name="choose_how" value="name" '
                  . ( $choose_how eq "name" ? "checked=\"1\" " : "" ) . '/>';

  print <<EOHTML;
    <form action="$self_url" method="GET">
      <p>Find me things on the way from:<br />
      $choose_os $origin_boxes to $dest_boxes<br />
      $choose_name $origin_list to $dest_list.</p>
      <input type="hidden" name="do_search" value="1">
      <input type="submit" name="Search" value="Search">
    </form>
EOHTML
}

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
  if ( $choose_how eq "name" ) {
    if ( !$origin || !$dest ) {
      print "<p>Must supply both origin and destination.</p>";
      return;
    }
  } elsif ( !$x1 || !$y1 || !$x2 || !$y2 ) {
    print "<p>Must supply x and y for both origin and destination.</p>";
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

  if ( $raw ) {
    print Dumper @candidates;
    exit 0;
  }

  if ( ! scalar @candidates ) {
    print "<p>Nothing found, sorry.</p>\n";
  } else {
    %tt_vars = (
                    x1       => $x1,
                    y1       => $y1,
                    x2       => $x2,
                    y2       => $y2,
                    nodes    => \@candidates,
                    long     => $q->param( "long" ) || $config->centre_long,
                    lat      => $q->param( "lat" ) || $config->centre_lat,
                    zoom     => $q->param( "zoom" )
                                    || $config->default_gmaps_zoom,
                    map_type => $q->param( "map_type" ) || "",
                    base_url => $config->script_url . $config->script_name,
                  );

    my $output;
    $tt = Template->new( { INCLUDE_PATH => "." } );
    $tt->process( "on-the-way.tt", \%tt_vars, \$output );
    $output ||= "<p>Failed to process template.</p>\n";
    print $output unless $raw;
  }
}

