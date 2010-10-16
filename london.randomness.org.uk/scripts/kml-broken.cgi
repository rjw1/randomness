#!/usr/bin/perl

use strict;
use warnings;

use lib "lib";

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use OpenGuides::Config;
use OpenGuides::Utils;
use Template;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my $q = CGI->new;

my $locale = $q->param( "locale" );

my $dbh = $wiki->store->dbh;

my $sql = "SELECT node.name, addr.metadata_value, lat.metadata_value,
                  long.metadata_value
           FROM node, metadata as addr, metadata as lat, metadata as long,
                metadata as loc
           WHERE node.id = addr.node_id AND node.version = addr.version
                 AND lower(addr.metadata_type) = 'address'
             AND node.id = lat.node_id AND node.version = lat.version
                 AND lower(lat.metadata_type) = 'latitude'
             AND node.id = long.node_id AND node.version = long.version
                 AND lower(long.metadata_type) = 'longitude'";
if ( $locale ) {
    $sql .= " AND node.id = loc.node_id AND node.version = loc.version
                  AND lower(loc.metadata_type) = 'locale'
                  AND lower(loc.metadata_value) = lower(?)";
}

my $sth = $dbh->prepare( $sql );

if ( $locale ) {
    $sth->execute( $locale ) or die $dbh->errstr;
} else {
    $sth->execute or die $dbh->errstr;
}

my $base_url = $config->script_url . $config->script_name . "?";

my @points;
while ( my ( $name, $addr, $lat, $long ) = $sth->fetchrow_array ) {
    my $url = $base_url . $formatter->node_name_to_node_param( $name );
    my $desc = qq( <a href="$url">$name</a><br />$addr );
    my ( $wgs84_long, $wgs84_lat ) = OpenGuides::Utils->get_wgs84_coords(
                                         latitude  => $lat,
                                         longitude => $long,
                                         config    => $config );
    push @points, { desc => $desc, wgs84_lat => $wgs84_lat,
                    wgs84_long => $wgs84_long };
}

my %tt_vars = ( points => \@points );

print $q->header( "application/vnd.google-earth.kml+xml" );
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH => ".:$custom_template_path:$template_path"  } );
$tt->process( "kml.tt", \%tt_vars );
