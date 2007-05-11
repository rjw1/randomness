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
my $length = $q->param( "length" );
$length =~ s/[^0-9]//g if $length;
$length ||= 200;
$q->param( -name => "length", -value => $length );

my $dbh = $wiki->store->dbh;
my $sql = "
SELECT node.name, locale.metadata_value, category.metadata_value
FROM node
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
WHERE char_length( node.text ) < ?
AND node.text NOT LIKE '%#REDIRECT%'
";

if ( $q->param( "exclude_locales" ) ) {
    $sql .= " AND node.name NOT LIKE 'Locale %'";
}
if ( $q->param( "exclude_categories" ) ) {
    $sql .= " AND node.name NOT LIKE 'Category %'";
}

my $sth = $dbh->prepare( $sql );
$sth->execute( $length ) or die $dbh->errstr;

my %locales;
my %categories;
my %pages;
while ( my ( $name, $this_locale, $this_category ) = $sth->fetchrow_array ) {
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
$tt_vars{length_box} = $q->textfield( -name => "length", -size => 5,
                                      -maxlength => 5 );

$tt_vars{exclude_locales_box} = $q->checkbox( -name => "exclude_locales",
                                              -value => 1, label => "" );
$tt_vars{exclude_categories_box} = $q->checkbox( -name => "exclude_categories",
                                                 -value => 1, label => "" );
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

my @short;
my $base_url = $config->script_url . $config->script_name . "?";
foreach my $page ( sort keys %pages ) {
  push @short, { url => $base_url
                        . $formatter->node_name_to_node_param( $page ),
                 name => CGI->escapeHTML( $page ) };
}

%tt_vars = (
             %tt_vars,
             addon_title => "Pages with short content",
             short       => \@short,
           );

print $q->header;
$tt->process( "short_content.tt", \%tt_vars );

