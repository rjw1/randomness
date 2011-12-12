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
use Wiki::Toolkit::Plugin::Categoriser;
use Wiki::Toolkit::Plugin::Locator::Grid;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;
my $dbh = $wiki->store->dbh;
my $locator = Wiki::Toolkit::Plugin::Locator::Grid->new( x => "os_x", y => "os_y" );
$wiki->register_plugin( plugin => $locator );
my $categoriser = Wiki::Toolkit::Plugin::Categoriser->new;
$wiki->register_plugin( plugin => $categoriser );

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;

my %all_criteria = (
                     vegan_friendly => "vegan friendly",
                     veggie_friendly => "vegetarian friendly",
                     totally_veggie => "totally vegetarian",
                     step_free => "step-free access",
                     accessible_loo => "accessible toilet",
                     restaurants_only => "restaurants",
                     cafes_only => "cafes",
                     takeaway => "takeaway",
                     delivery => "takeaway delivery",
                     indian_food => "indian food",
                     vietnamese_food => "vietnamese food",
                     delivers_to_se16 => "delivers to se16",
                   );

setup_form_variables();

if ( $q->param( "Search" ) ) {
  $tt_vars{doing_search} = 1;
  my @dbparams;
  my $locale = $q->param( "locale" );
  my $district = $q->param( "postal_district" );
  my $tube = $q->param( "tube" );
  my %criteria;

  foreach my $criterion ( keys %all_criteria ) {
    $criteria{$criterion} = $q->param( $criterion );
  }

  my %candidates;
  if ( $tube ) {
    my @cand_arr = $locator->find_within_distance(
        node => $tube,
        metres => $q->param( "tube_distance" ) || 750,
    );
    %candidates = map { $_ =>1 } @cand_arr;
  }

  my $sql = "
SELECT DISTINCT node.name, summary.metadata_value FROM node
INNER JOIN metadata as cat
  ON ( node.id = cat.node_id AND node.version = cat.version
       AND lower(cat.metadata_type) = 'category'
       AND (
";

  my @foodcats = ( "restaurants", "cafes", "food served lunchtimes",
                   "food served evenings", "pub food", "takeaway" );
  @foodcats = map { "lower(cat.metadata_value) = '" . lc($_) . "'"; }
              @foodcats;
  $sql .= join " OR ", @foodcats;

  $sql .="
           )
     )
INNER JOIN metadata as summary
  ON ( node.id = summary.node_id AND node.version = summary.version
       AND lower( summary.metadata_type ) = 'summary'
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

  my @results;
  while ( my ( $name, $summary ) = $sth->fetchrow_array ) {
    if ( !$tube or $candidates{$name} ) {
      my $param = $formatter->node_name_to_node_param( $name );
      push @results, { name => $name, param => $param, summary => $summary };
    }
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
             addon_title => "Food search",
           );

print $q->header;
$tt->process( "foodsearch.tt", \%tt_vars );

sub setup_form_variables {

  $tt_vars{tube_distance_box} = $q->popup_menu( -name   => "tube_distance",
                                         -values => [ 500, 750, 1000, 1500,
                                                      2000 ],
                                         -labels => { 500 => "500m",
                                                      750 => "750m",
                                                      1000 => "1km",
                                                      1500 => "1.5km",
                                                      2000 => "2km",
                                                    },
                                       );

  # Find all locales.  Maybe later we can filter on locales that we'll actually
  # get some results for.
  my @all_locales = $wiki->list_nodes_by_metadata(
        metadata_type  => "category",
        metadata_value => "locales",
        ignore_case    => 1,
  );

  my %locales;
  my %postal_districts;
  foreach my $locale ( @all_locales ) {
    $locale =~ s/^Locale //;
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

  $tt_vars{tube_box} = RGL::Addons->get_tube_dropdown( guide => $guide, q => $q );
}
