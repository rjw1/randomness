#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "lib";

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use OpenGuides::Config;
use OpenGuides::Utils;
use RGL::Addons;
use Template;
use Wiki::Toolkit::Plugin::Locator::Grid;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;
my $dbh = $wiki->store->dbh;
my $locator = Wiki::Toolkit::Plugin::Locator::Grid->new( x => "os_x", y => "os_y" );
$wiki->register_plugin( plugin => $locator );

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;

setup_form_variables();

my $pageno = $q->param( "pageno" ) || "";
$pageno =~ s/[^0-9]//g;

if ( $pageno ) {
  $tt_vars{doing_search} = 1;

  my $sql = "
SELECT node.name, address.metadata_value, x.metadata_value, y.metadata_value,
       lat.metadata_value, long.metadata_value
FROM node
INNER JOIN metadata as address
  ON ( node.id = address.node_id AND node.version = address.version
       AND lower( address.metadata_type ) = 'address'
     )
INNER JOIN metadata as x
  ON ( node.id = x.node_id AND node.version = x.version
       AND lower( x.metadata_type ) = 'os_x'
     )
INNER JOIN metadata as y
  ON ( node.id = y.node_id AND node.version = y.version
       AND lower( y.metadata_type ) = 'os_y'
     )
INNER JOIN metadata as lat
  ON ( node.id = lat.node_id AND node.version = lat.version
       AND lower( lat.metadata_type ) = 'latitude'
     )
INNER JOIN metadata as long
  ON ( node.id = long.node_id AND node.version = long.version
       AND lower( long.metadata_type ) = 'longitude'
     )
WHERE x.metadata_value::integer >= ?
AND   x.metadata_value::integer <= ?
AND   y.metadata_value::integer >= ?
AND   y.metadata_value::integer <= ?
ORDER BY name";

  my @limits = get_page_limits( $pageno );
#use Data::Dumper; print Dumper \@limits; exit 0;

  my $sth = $dbh->prepare( $sql );
  $sth->execute( @limits ) or die $dbh->errstr;

  my @results;
  while ( my ( $name, $address, $x, $y, $lat, $long )
                                                 = $sth->fetchrow_array ) {
    my $param = $formatter->node_name_to_node_param( $name );
    my ( $wgs84_long, $wgs84_lat ) = OpenGuides::Utils->get_wgs84_coords(
                                        latitude  => $lat,
                                        longitude => $long,
                                        config    => $config );
    push @results, { name => $name, param => $param, address => $address,
                     x => $x, y => $y, wgs84_lat => $wgs84_lat,
                     wgs84_long => $wgs84_long };
  }

  $tt_vars{results} = \@results;
}

# Do the template stuff.
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );
%tt_vars = (
             %tt_vars,
             addon_title => "A-Z search",
             exclude_navbar      => 1,
             enable_gmaps        => 1,
             display_google_maps => 1,
             lat                 => $config->centre_lat,
             long                => $config->centre_long,
             zoom                => $config->default_gmaps_zoom,
           );

print $q->header;
$tt->process( "a_z_search.tt", \%tt_vars );

sub setup_form_variables {
  $tt_vars{page_no_box} = $q->textfield( -name => "pageno", -size => 3,
                                         -maxlength => 3 );
}

sub get_page_limits {
  my $pageno = shift;

  my %corners = (
                  20  => [ 523.5, 198 ],
                  26  => [ 513.5, 194.5 ],
                  38  => [ 506, 191 ],
                  56  => [ 506, 187.5 ],
                  74  => [ 506, 184 ],
                  92  => [ 506, 180.5 ],
                  110 => [ 506, 177 ],
                  128 => [ 506, 173.5 ],
                  146 => [ 506, 170 ],
                  162 => [ 516, 166.5 ],
                );

  if ( $corners{$pageno} ) {
    my ( $x1, $y2 ) = @{$corners{$pageno}};
    return ( $x1 * 1000, ($x1 + 2.5) * 1000, ($y2 - 3.5) * 1000, $y2 * 1000 );
  }

  foreach my $cornerno ( reverse sort keys %corners ) {
    if ( $cornerno < $pageno ) {
      my $diff = $pageno - $cornerno;
      my ( $cx1, $y2 ) = @{$corners{$cornerno}};
      my $x1 = $cx1 + ( $diff * 2.5 );
      return ( $x1 * 1000, ($x1 + 2.5) * 1000, ($y2 - 3.5) * 1000, $y2 * 1000 );
    }
  }

}
