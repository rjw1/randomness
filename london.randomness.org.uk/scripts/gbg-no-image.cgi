#!/usr/bin/perl

use strict;
use warnings;

use lib qw( /export/home/rgl/web/vhosts/london.randomness.org.uk/scripts/lib/ );
use lib qw( /export/home/rgl/perl5/lib/perl5 );
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

my $dbh = $wiki->store->dbh;
my $sql = "
SELECT node.name, ml.metadata_value FROM node
INNER JOIN metadata as mgbg
  ON ( node.id=mgbg.node_id
       AND node.version=mgbg.version
       AND lower(mgbg.metadata_type) = 'category'
       AND lower(mgbg.metadata_value) = 'good beer guide'
     )
INNER JOIN metadata as ml
  ON ( node.id = ml.node_id
       AND node.version = ml.version
       AND lower(ml.metadata_type) = 'locale'
     )
";

my $sth = $dbh->prepare( $sql );
$sth->execute or die $dbh->errstr;

my %data;
my %locales;
while ( my ( $name, $this_locale ) = $sth->fetchrow_array ) {
  $locales{$this_locale} = 1;
  if ( $locale && ( lc( $this_locale ) ne lc( $locale ) ) ) {
    next;
  }
  if ( $data{$name} ) {
    push @{$data{$name}}, $this_locale;
  } else {
    $data{$name} = [ $this_locale ];
  }
}

my @localelist = map { s/^Locale //; $_; } keys %locales;
@localelist = sort( @localelist );

my $any_string = " -- any -- ";
$tt_vars{locale_box} = $q->popup_menu( -name   => "locale",
                                       -values => [ "", @localelist ],
                                       -labels => { "" => $any_string,
                                                    map { $_ => $_ }
                                                          @localelist },
                                     );
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

my @pubs = keys %data;
@pubs = sort @pubs;

my @lacking;
my $base_url = $config->script_url . $config->script_name . "?";
foreach my $pub ( @pubs ) {
  my %data = $wiki->retrieve_node( $pub );
  if ( !$data{metadata}{node_image} ) {
    push @lacking, { url => $base_url
                            . $formatter->node_name_to_node_param( $pub ),
                     name => CGI->escapeHTML( $pub ) };
  }
}

%tt_vars = (
             %tt_vars,
             addon_title => "Good Beer Guide pubs without a photo",
             all         => \@pubs,
             lacking     => \@lacking,
           );

print $q->header;
$tt->process( "missing_images.tt", \%tt_vars );

