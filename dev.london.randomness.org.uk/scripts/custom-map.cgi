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
use Wiki::Toolkit::Plugin::Locator::Grid;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;
my $dbh = $wiki->store->dbh;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;

setup_form_variables();

# Do the template stuff.
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );
%tt_vars = (
             %tt_vars,
             addon_title         => "Create a custom map",
             enable_gmaps        => 1,
             display_google_maps => 1,
             show_map            => 1,
             lat                 => $config->centre_lat,
             long                => $config->centre_long,
             zoom                => $config->default_gmaps_zoom,
           );

print $q->header;
$tt->process( "custom_map.tt", \%tt_vars );

sub setup_form_variables {

  my @all_nodes = RGL::Addons->get_nodes_with_geodata( wiki => $wiki,
                                                       config => $config,
                                                       return_latlong => 1,
                                                     );
  my %choices = map { $_->{name} => $_->{name} } @all_nodes;
  $tt_vars{node_list} = $q->popup_menu( -name   => "nodes",
                                        -id     => "node_list",
                                        -values => [ "", sort keys %choices ],
                                        -labels => { "" => " -- choose -- ",
                                                     %choices },
                                      );

  $tt_vars{node_data} = \@all_nodes;
}
