#!/usr/bin/perl

use strict;
use warnings;

use lib qw( /export/home/rgl/web/vhosts/london.randomness.org.uk/scripts/lib/ );
use lib qw( /export/home/rgl/perl5/lib/perl5 );
use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use OpenGuides::Config;
use OpenGuides::Utils;
use RGL::Addons;
use Template;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;

$tt_vars{self_url} = $q->url( -relative );
$tt_vars{show_search_example} = 1;
setup_form_fields();

my $do_search = $q->param( "Search" );
my $cat = $q->param( "cat" );
my $loc = $q->param( "loc" );

if ( $do_search || $cat || $loc ) {
  if ( !$loc ) {
    $loc = "Croydon";
  }
  $tt_vars{show_search_example} = 0;
  my $small_pointers = $q->param( "small_pointers" ) || 0;
  my $blue_pointers = $q->param( "blue_pointers" ) || 0;
  my $show_map = $q->param( "map" );
  my $map_style = $q->param( "map_style" );

  if ( !$cat && !$loc ) {
  } else {
    $tt_vars{do_search} = 1;
    $tt_vars{cat} = $cat;
    $tt_vars{loc} = $loc;

    my $base_url = $config->script_url . $config->script_name;
    $tt_vars{cat_link} = $base_url . "?" . $formatter->node_name_to_node_param(
                         "Category " . $cat );
    $tt_vars{loc_link} = $base_url . "?" . $formatter->node_name_to_node_param(
                         "Locale " . $loc );

    my $dbh = $wiki->store->dbh;
    my $sql = "
      SELECT DISTINCT node.id, node.name, mlat.metadata_value as lat,
                 mlong.metadata_value as 'long'
      FROM node";
    if ( $cat ) {
      $sql .= "
      INNER JOIN metadata as mcat
        ON ( node.id=mcat.node_id
             AND node.version=mcat.version
             AND lower(mcat.metadata_type)='category'
             AND lower(mcat.metadata_value)=? )";
    }
    if ( $loc ) {
      $sql .= "
      INNER JOIN metadata as mloc
        ON ( node.id=mloc.node_id
             AND node.version=mloc.version
             AND lower(mloc.metadata_type)='locale'
             AND lower(mloc.metadata_value)=? )";
    }
    $sql .= "
      INNER JOIN metadata as mlat
        ON ( node.id=mlat.node_id
             AND node.version=mlat.version
             AND lower(mlat.metadata_type)='latitude' )
      INNER JOIN metadata as mlong
        ON ( node.id=mlong.node_id
             AND node.version=mlong.version
             AND lower(mlong.metadata_type)='longitude' )
      ORDER BY node.name";

    my $markertype;
    if ( $blue_pointers ) {
      if ( $small_pointers ) {
        $markertype = "small_light_blue";
      } else {
        $markertype = "large_light_blue";
      }
    } else {
      if ( $small_pointers ) {
        $markertype = "small_light_red";
      } else {
        $markertype = "large_light_red";
      }
    }

    my @results;
    my ( $min_lat, $max_lat, $min_long, $max_long, $bd_set );
    my $sth = $dbh->prepare( $sql );
    if ( $cat && $loc ) {
      $sth->execute( lc( $cat ), lc( $loc ) ) or die $dbh->errstr;
    } elsif ( $cat ) {
      $sth->execute( lc( $cat ) ) or die $dbh->errstr;
    } elsif ( $loc ) {
      $sth->execute( lc( $loc ) ) or die $dbh->errstr;
    }
    while ( my ( $id, $name, $lat, $long ) = $sth->fetchrow_array ) {
      my $url = $base_url . "?" . $formatter->node_name_to_node_param( $name );
      if ( $show_map ) {
        # I still hate that I have to do this.
        ( $long, $lat ) = OpenGuides::Utils->get_wgs84_coords(
                                        latitude  => $lat,
                                        longitude => $long,
                                        config    => $config );
      }
      push @results, { id => $id, name => $name, url => $url,
                       lat => $lat, long => $long, markertype => $markertype };
      if ( !$bd_set ) {
        $min_lat = $max_lat = $lat;
        $min_long = $max_long = $long;
        $bd_set = 1;
      } else {
        if ( $lat < $min_lat ) {
          $min_lat = $lat;
        }
        if ( $long < $min_long ) {
          $min_long = $long;
        }
        if ( $lat > $max_lat ) {
          $max_lat = $lat;
        }
        if ( $long > $max_long ) {
          $max_long = $long;
        }
      }
    }

    $tt_vars{results} = \@results;

    if ( $show_map ) {
      %tt_vars = (
                   %tt_vars,
                   min_lat             => $min_lat,
                   max_lat             => $max_lat,
                   min_long            => $min_long,
                   max_long            => $max_long,
                   exclude_navbar      => 1,
                   enable_gmaps        => 1,
                   display_google_maps => 1,
                   show_map            => 1,
                   map_style           => $map_style,
                   lat                 => ( $min_lat + $max_lat ) / 2,
                   long                => ( $min_long + $max_long ) / 2,
                 );
    }
  }
}

$tt_vars{addon_title} = "Locale/Category Search";
print $q->header;
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH => ".:$custom_template_path:$template_path"  } );
$tt->process( "locate.tt", \%tt_vars );

sub setup_form_fields {
  my @categories = $wiki->list_nodes_by_metadata(
    metadata_type  => "category",
    metadata_value => "category",
    ignore_case    => 1,
  );
  @categories = map { s/^Category //; $_; } @categories;
  my %tmphash = map { $_ => 1 } @categories;
  for my $key ( ( "Breweries", "Category", "Drink", "Food", "Locales", "Meta", "Now Closed", "Postal Districts", "Pub Chains", "Pub Crawls", "Streets", "Travel", "Wifi" ) ) {
    delete $tmphash{ $key };
  }
  @categories = sort( keys %tmphash );

  $tt_vars{catbox} = $q->popup_menu( -name   => "cat",
                                -values => [ "", @categories ],
                                -labels => { "" => " -- anything -- ",
                                             map { $_ => $_ } @categories }
                              );

  my @locales = $wiki->list_nodes_by_metadata(
    metadata_type  => "category",
    metadata_value => "locales",
    ignore_case    => 1,
  );
  @locales = map { s/^Locale //; $_; } @locales;
  @locales = sort( @locales );

  $tt_vars{locbox} = $q->popup_menu( -name   => "loc",
                                -values => [ "", @locales ],
                                -labels => { "" => " -- anywhere -- ",
                                             map { $_ => $_ } @locales }
                              );

  $tt_vars{show_map_box} = $q->checkbox( -name => "map",
                                         -value => 1, label => "" );
  $tt_vars{small_pointers_box} = $q->checkbox( -name => "small_pointers",
                                               -value => 1, label => "" );
  $tt_vars{blue_pointers_box} = $q->checkbox( -name => "blue_pointers",
                                               -value => 1, label => "" );
  $tt_vars{map_style_group} = $q->radio_group(
      -name => "map_style",
      -values => [ "mq", "osm", "watercolour", "google" ],
      -default => "mq",
      -labels => { "mq" => "MapQuest", "osm" => "OpenStreetMap",
                   "watercolour" => "Stamen Watercolour",
                   "google" => "Google Maps" },
  );
}
