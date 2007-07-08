#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "lib";

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use RGL::Addons;
use OpenGuides::Config;
use Template;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;

my $locale = $q->param( "locale" );
my $category = $q->param( "category" );
my $os_x = $q->param( "os_x" );
my $os_y = $q->param( "os_y" );
my $os_dist = $q->param( "os_dist" );
my $origin = $q->param( "origin" );
my $origin_dist = $q->param( "origin_dist" );

if ( $origin && defined $origin_dist ) {
    my %data = $wiki->retrieve_node( $origin );
    my $x = $data{metadata}{os_x}[0];
    my $y = $data{metadata}{os_y}[0];
    if ( $x && $y ) {
        $os_x = $x;
        $os_y = $y;
        $os_dist = $origin_dist;
    }
}

$os_x =~ s/[^0-9]//g if $os_x;
$os_y =~ s/[^0-9]//g if $os_y;
$os_dist =~ s/[^0-9]//g if $os_dist;

my $dbh = $wiki->store->dbh;
my $sql = "
SELECT node.name, locale.metadata_value, category.metadata_value, node.text,
       x.metadata_value, y.metadata_value
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
       AND lower( x.metadata_type ) = 'os_x'
     )
LEFT JOIN metadata as y
  ON ( node.id = y.node_id
       AND node.version = y.version
       AND lower( y.metadata_type ) = 'os_y'
     )
WHERE img.metadata_value IS NULL
";

if ( $q->param( "exclude_locales" ) ) {
  $sql .= " AND node.name NOT LIKE 'Locale %'";
}
if ( $q->param( "exclude_categories" ) ) {
  $sql .= " AND node.name NOT LIKE 'Category %'";
}

my $sth = $dbh->prepare( $sql );
$sth->execute or die $dbh->errstr;

my %locales;
my %categories;
my %pages;
while ( my ( $name, $this_locale, $this_category, $content, $x, $y )
                                                     = $sth->fetchrow_array ) {
    if ( $content =~ qr/^\s*#REDIRECT/ ) {
        next;
    }
    if ( $this_locale ) {
        $locales{$this_locale} = 1;
    }
    if ( $this_category ) {
        $categories{$this_category} = 1;
    }
    if ( $locale && ( lc( $this_locale ) ne lc( $locale ) ) ) {
        next;
    }
    if ( $category && ( lc( $this_category ) ne lc( $category ) ) ) {
        next;
    }
    if ( $os_x && $os_y && $os_dist ) {
        if ( !$x || !$y ) {
            next;
        }
        my $dist = int( sqrt( ( $os_x - $x )**2 + ( $os_y - $y )**2 ) + 0.5 );
        if ( $dist > $os_dist ) {
            next;
        }
    }
    $pages{$name} = 1;
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
$tt_vars{os_x_box} = $q->textfield( -name => "os_x", -size => 6,
                                    -maxlength => 6 );
$tt_vars{os_y_box} = $q->textfield( -name => "os_y", -size => 6,
                                    -maxlength => 6 );
$tt_vars{os_dist_box} = $q->textfield( -name => "os_dist", -size => 4,
                                       -maxlength => 4 );

my @all_nodes = RGL::Addons->get_nodes_with_geodata( wiki => $wiki );
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
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

my @lacking;
my $base_url = $config->script_url . $config->script_name . "?";
foreach my $page ( sort keys %pages ) {
  push @lacking, { url => $base_url
                          . $formatter->node_name_to_node_param( $page ),
                   name => CGI->escapeHTML( $page ) };
}

%tt_vars = (
             %tt_vars,
             addon_title => "Pages without a photo",
             lacking     => \@lacking,
           );

print $q->header;
$tt->process( "no_image.tt", \%tt_vars );

