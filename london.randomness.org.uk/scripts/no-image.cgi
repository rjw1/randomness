#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "lib";

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use Geo::HelmertTransform;
use OpenGuides;
use POSIX;
use RGL::Addons;
use OpenGuides::Config;
use OpenGuides::Utils;
use Template;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );
my $geo_handler = $config->geo_handler;

my $q = CGI->new;

my $locale = $q->param( "locale" );
my $category = $q->param( "category" );
my $os_x = $q->param( "os_x" );
my $os_y = $q->param( "os_y" );
my $os_dist = $q->param( "os_dist" );
my $lat = $q->param( "latitude" );
my $long = $q->param( "longitude" );
my $latlong_dist = $q->param( "latlong_dist" );
my $origin = $q->param( "origin" );
my $origin_dist = $q->param( "origin_dist" );
my $show_map = $q->param( "show_map" );

my ( $x, $y, $dist );

if ( $origin && defined $origin_dist ) {
    my %data = $wiki->retrieve_node( $origin );
    if ( $geo_handler == 3 ) {
        my $mx = $data{metadata}{easting}[0];
        my $my = $data{metadata}{northing}[0];
        if ( $mx && $my ) {
            $x = $mx;
            $y = $my;
            $dist = $origin_dist;
        }
    } elsif ( $geo_handler == 1 ) {
        my $mx = $data{metadata}{os_x}[0];
        my $my = $data{metadata}{os_y}[0];
        if ( $mx && $my ) {
            $x = $mx;
            $y = $my;
            $dist = $origin_dist;
        }
    }
} else {
    if ( $os_x && $os_y && $os_dist && ( $geo_handler == 1 ) ) {
        $x = $os_x;
        $y = $os_y;
        $dist = $os_dist;
    } elsif ( $lat && $long && $latlong_dist && ( $geo_handler == 3 ) ) {
        require Geo::Coordinates::UTM;
        my $zone;
        ($zone, $x, $y ) = 
                     Geo::Coordinates::UTM::latlon_to_utm( $config->ellipsoid, 
                                                           $lat, $long ); 
        $x =~ s/\..*//; # chop off decimal places 
        $y =~ s/\..*//; # - metre accuracy enough
        $dist = $latlong_dist;
    }
}

$x =~ s/[^0-9]//g if $x;
$y =~ s/[^0-9]//g if $y;
$dist =~ s/[^0-9]//g if $dist;

my ( $x_name, $y_name );
if ( $geo_handler == 3 ) {
    $x_name = "easting";
    $y_name = "northing";
} elsif ( $geo_handler == 1 ) {
    $x_name = "os_x";
    $y_name = "os_y";
}

my $dbh = $wiki->store->dbh;
my $sql = "
SELECT DISTINCT
       node.name, locale.metadata_value, category.metadata_value, node.text,
       x.metadata_value, y.metadata_value,
       latit.metadata_value, longit.metadata_value
FROM node
LEFT JOIN metadata as img
  ON ( node.id = img.node_id
       AND node.version = img.version
       AND lower( img.metadata_type ) = 'node_image'
     )
LEFT JOIN metadata as locale
  ON ( node.id = locale.node_id
       AND node.version = locale.version
       AND lower( locale.metadata_type ) = 'locale'
     )
LEFT JOIN metadata as category
  ON ( node.id = category.node_id
       AND node.version = category.version
       AND lower( category.metadata_type ) = 'category'
     )
LEFT JOIN metadata as x
  ON ( node.id = x.node_id
       AND node.version = x.version
       AND lower( x.metadata_type ) = '$x_name'
     )
LEFT JOIN metadata as y
  ON ( node.id = y.node_id
       AND node.version = y.version
       AND lower( y.metadata_type ) = '$y_name'
     )
LEFT JOIN metadata as latit
  ON ( node.id = latit.node_id
       AND node.version = latit.version
       AND lower( latit.metadata_type ) = 'latitude'
     )
LEFT JOIN metadata as longit
  ON ( node.id = longit.node_id
       AND node.version = longit.version
       AND lower( longit.metadata_type ) = 'longitude'
     )
WHERE img.metadata_value IS NULL
";

if ( $q->param( "exclude_locales" ) ) {
  $sql .= " AND node.name NOT LIKE 'Locale %'";
}
if ( $q->param( "exclude_categories" ) ) {
  $sql .= " AND node.name NOT LIKE 'Category %'";
}

$sql .= " ORDER BY node.name";

my $sth = $dbh->prepare( $sql );
$sth->execute or die $dbh->errstr;

my %locales;
my %categories;
my %results;
my $base_url = $config->script_url . $config->script_name . "?";
my $total_count; # Everything with missing photo even if not on map.

while ( my ( $name, $this_locale, $this_category, $content,
             $this_x, $this_y, $this_lat, $this_long)
                                                     = $sth->fetchrow_array ) {
    # If this is a redirect it doesn't count at all.
    if ( $content =~ qr/^\s*#REDIRECT/ ) {
        next;
    }

    # Make sure to grab the categories and locales for our list of cats/locs
    # that have missing images.
    if ( $this_locale ) {
        $locales{$this_locale} = 1;
    }
    if ( $this_category ) {
        $categories{$this_category} = 1;
    }

    # We may have already processed this page, if it has more than one locale
    # or category.
    if ( $results{$name} ) {
        next;
    }

    # Check the criteria.
    if ( $locale && ( lc( $this_locale ) ne lc( $locale ) ) ) {
        next;
    }
    if ( $category && ( lc( $this_category ) ne lc( $category ) ) ) {
        next;
    }

    # If we're doing a location search, we need geodata.
    if ( $x && $y && $dist ) {
        if ( !$this_x || !$this_y ) {
            next;
        }
        my $this_dist = int( sqrt( ( $x - $this_x )**2 + ( $y - $this_y )**2 )
                             + 0.5 );
        if ( $this_dist > $dist ) {
            next;
        }
    }

    # OK, this should definitely be included in the count.
    $total_count++;

    # But not on the map, if we want a map and it has no coords.
    if ( $show_map ) {
        if ( !$this_lat || !$this_long ) {
            next;
        }
    }

    # OK, we want to include this page; package its data for TT.
    my $param = $formatter->node_name_to_node_param( $name );
    my $this = {
                 name => CGI->escapeHTML( $name ),
                 url  => $base_url . $param,
               };
    if ( defined $this_lat && defined $this_long ) {
        ( $this_long, $this_lat ) = OpenGuides::Utils->get_wgs84_coords(
                                        latitude  => $this_lat,
                                        longitude => $this_long,
                                        config    => $config );
        $this->{lat} = $this_lat;
        $this->{long} = $this_long;
    }
    $results{$name} = $this;
}

my $any_string = " -- any -- ";

my @localelist = map { s/^Locale //; $_; } keys %locales;
@localelist = sort( @localelist );
$tt_vars{locale_box} = $q->popup_menu( -name   => "locale",
                                       -values => [ "", @localelist ],
                                       -labels => { "" => $any_string,
                                                    map { $_ => $_ }
                                                          @localelist },
                                     );
my @catlist = map { s/^Category //; $_; } keys %categories;
@catlist = sort( @catlist );
$tt_vars{category_box} = $q->popup_menu( -name   => "category",
                                         -values => [ "", @catlist ],
                                         -labels => { "" => $any_string,
                                                      map { $_ => $_ }
                                                            @catlist },
                                       );

if ( $geo_handler == 1 ) {
    $tt_vars{os_x_box} = $q->textfield( -name => "os_x", -size => 6,
                                        -maxlength => 6 );
    $tt_vars{os_y_box} = $q->textfield( -name => "os_y", -size => 6,
                                        -maxlength => 6 );
    $tt_vars{os_dist_box} = $q->textfield( -name => "os_dist", -size => 4,
                                           -maxlength => 4 );
} elsif ( $geo_handler == 3 ) {
    $tt_vars{latitude_box} = $q->textfield( -name => "latitude", -size => 10 );
    $tt_vars{longitude_box} = $q->textfield( -name => "longitude", -size => 10 );
    $tt_vars{latlong_dist_box} = $q->textfield( -name => "latlong_dist",
                                                -size => 4, -maxlength => 4 );
}

my @all_nodes = RGL::Addons->get_nodes_with_geodata( wiki => $wiki,
                                                     config => $config );
my %choices = map { $_->{name} => $_->{name} } @all_nodes;
$tt_vars{origin_list} = $q->popup_menu( -name   => "origin",
                                        -values => [ "", sort keys %choices ],
                                        -labels => { "" => " -- choose -- ",
                                                     %choices },
                                      );
$tt_vars{origin_dist_box} = $q->textfield( -name => "origin_dist", -size => 4,
                                           -maxlength => 4 );

$tt_vars{exclude_locales_box} = $q->checkbox( -name => "exclude_locales",
                                              -value => 1, label => "" );
$tt_vars{exclude_categories_box} = $q->checkbox( -name => "exclude_categories",
                                                 -value => 1, label => "" );
$tt_vars{show_map_box} = $q->checkbox( -name => "show_map",
                                                 -value => 1, label => "" );
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

# Make sure the maps work, and include the total count in case some had to
# be missed off the map.
if ( $show_map ) {
    %tt_vars = (
                 %tt_vars,
                 enable_gmaps        => 1,
                 display_google_maps => 1,
                 show_map            => 1,
                 lat                 => $config->centre_lat,
                 long                => $config->centre_long,
                 zoom                => $config->default_gmaps_zoom,
                 total_count         => $total_count,
               );
}

# Grab the total number of photos and pages.
my $num_photos = RGL::Addons->get_num_photos( wiki => $wiki );
$tt_vars{num_photos} = $num_photos;
my $num_pages = RGL::Addons->get_page_count( wiki => $wiki );
$tt_vars{percent_photos} = floor( 100 * $num_photos / $num_pages );

%tt_vars = (
             %tt_vars,
             addon_title => "Pages without a photo",
             geo_handler => $geo_handler,
             results     => [ sort { $a->{name} cmp $b->{name} }
                                   values %results ],
           );

if ( $q->param( "format" ) && $q->param( "format" ) eq "kml" ) {
    $tt_vars{points} = $tt_vars{results};
    $tt_vars{style} = "photo";
    print $q->header( "application/vnd.google-earth.kml+xml" );
    $tt->process( "kml.tt", \%tt_vars );
} else {
    print $q->header;
    $tt->process( "no_image.tt", \%tt_vars ) or die $tt->error;
}
