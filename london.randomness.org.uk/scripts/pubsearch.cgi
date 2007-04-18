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
my $dbh = $wiki->store->dbh;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;

my %all_criteria = (
                     garden    => "beer gardens",
                     realale   => "real ale",
                     realcider => "real cider",
                     gbg       => "good beer guide",
                     wifi      => "free wireless",
                     lunch     => "food served lunchtimes",
                     dinner    => "food served evenings",
                   );

setup_form_variables();

if ( $q->param( "Search" ) ) {
  $tt_vars{doing_search} = 1;
  my @dbparams;
  my $locale = $q->param( "locale" );
  my $district = $q->param( "postal_district" );
  my %criteria;

  foreach my $criterion ( keys %all_criteria ) {
    $criteria{$criterion} = $q->param( $criterion );
  }

  my $sql = "
SELECT node.name FROM node
INNER JOIN metadata as pub
  ON ( node.id = pub.node_id AND node.version = pub.version
       AND lower(pub.metadata_type) = 'category'
       AND lower(pub.metadata_value) = 'pubs'
     )
";

  if ( $locale || $district ) {
    $sql .= "
INNER JOIN metadata as locale
  ON ( node.id = locale.node_id AND node.version = locale.version
       AND lower(locale.metadata_type) = 'locale'
       AND lower(locale.metadata_value) = ? )
";
    if ( $locale ) {
      push @dbparams, lc( $locale );
    } else {
      push @dbparams, lc( $district );
    }
  }

  foreach my $criterion ( keys %all_criteria ) {
    if ( $criteria{$criterion} ) {
      $sql .= "
INNER JOIN metadata AS $criterion
  ON ( node.id = $criterion.node_id AND node.version = $criterion.version
       AND lower($criterion.metadata_type) = 'category'
       AND lower($criterion.metadata_value) = ? )
";
      push @dbparams, lc( $all_criteria{$criterion} );
    }
  }

  $sql .= " ORDER BY name";

  $tt_vars{sql} = $q->escapeHTML( $sql );

  my $sth = $dbh->prepare( $sql );
  $sth->execute( @dbparams ) or die $dbh->errstr;

  my @pubs;
  while ( my ( $pub ) = $sth->fetchrow_array ) {
    my $param = $formatter->node_name_to_node_param( $pub );
    push @pubs, { name => $pub, param => $param };
  }

  $tt_vars{pubs} = \@pubs;
}

# Do the template stuff.
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );
%tt_vars = (
             %tt_vars,
             addon_title => "Pub search",
           );

print $q->header;
$tt->process( "pubsearch.tt", \%tt_vars );

sub setup_form_variables {

  # Find all locales that have pubs in.
  my $sql = "
  SELECT DISTINCT locale.metadata_value FROM node
  INNER JOIN metadata as pub
    ON ( node.id=pub.node_id
         AND node.version=pub.version
         AND lower(pub.metadata_type) = 'category'
         AND lower(pub.metadata_value) = 'pubs'
       )
  INNER JOIN metadata as locale
    ON ( node.id = locale.node_id
         AND node.version = locale.version
         AND lower(locale.metadata_type) = 'locale'
       )
  ";

  my $sth = $dbh->prepare( $sql );
  $sth->execute or die $dbh->errstr;

  my %locales;
  my %postal_districts;
  while ( my ( $locale ) = $sth->fetchrow_array ) {
    if ( $locale =~ /^[A-Z][A-Z]?[0-9][0-9]?$/ ) {
      $postal_districts{$locale} = 1;
    } else {
      $locales{$locale} = 1;
    }
  }

  my $any_string = " -- any -- ";
  my @localelist = sort keys %locales;
  $tt_vars{locale_box} = $q->popup_menu( -name   => "locale",
                                         -values => [ "", @localelist ],
                                         -labels => { "" => $any_string,
                                                      map { $_ => $_ }
                                                            @localelist },
                                       );

  my @postallist = sort keys %postal_districts;
  $tt_vars{postal_district_box} =
                         $q->popup_menu( -name   => "postal_district",
                                         -values => [ "", @postallist ],
                                         -labels => { "" => $any_string,
                                                      map { $_ => $_ }
                                                            @postallist },
                                       );

  my %checkboxes;
  foreach my $criterion ( keys %all_criteria ) {
    $checkboxes{$criterion} = $q->checkbox( -name => $criterion,
                                            -value => 1, -label => "" );
  }

  $tt_vars{checkboxes} = \%checkboxes;
}
  