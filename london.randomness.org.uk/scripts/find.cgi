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
my $locator = Wiki::Toolkit::Plugin::Locator::Grid->new( x => "os_x", y => "os_y" );
$wiki->register_plugin( plugin => $locator );
my $formatter = $wiki->formatter;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );
my $geo_handler = $config->geo_handler;

my $q = CGI->new;

if ( !$q->param( "do_search" ) ) {
    $tt_vars{show_search_example} = 1;
}
$tt_vars{self_url} = $q->url( -relative );
setup_form_fields();

if ( $q->param( "do_search" ) ) {
  my $cat1 = $q->param( "cat1" );
  my $cat2 = $q->param( "cat2" );
  my $dist = $q->param( "distance" );

  my $show_map = $q->param( "show_map" );

  $dist ||= 0;
  $dist =~ s/[^0-9]//g;

  if ( !$dist || !$cat1 ) {
    # Yes, the categories are displayed the wrong way around.  Don't want to
    # break URLs, so don't change it.
    $tt_vars{error_message} =
                  "Must supply at least the second category, and a distance.";
  } else {
    $tt_vars{do_search} = 1;
    $tt_vars{cat1} = $cat1;
    $tt_vars{cat2} = $cat2;

    my $base_url = $config->script_url . $config->script_name;

    my $dbh = $wiki->store->dbh;
    my %sql;
    foreach my $key ( qw( cat1 cat2 ) ) {
	$sql{$key} = "
          SELECT DISTINCT node.id, node.name, mx.metadata_value as x,
                 my.metadata_value as y, mlat.metadata_value as lat,
                 mlong.metadata_value as long
          FROM node
          INNER JOIN metadata as mc
            ON ( node.id=mc.node_id
                 AND node.version=mc.version
                 AND lower(mc.metadata_type)='category'";
      if ( $key eq "cat1" || ( $key eq "cat2" && $cat2 ) ) {
          $sql{$key} .= " AND lower(mc.metadata_value)=? ";
      }
      $sql{$key} .= "
               )
          INNER JOIN metadata as mx
            ON ( node.id=mx.node_id
                 AND node.version=mx.version
                 AND lower(mx.metadata_type)='os_x' )
          INNER JOIN metadata as my
            ON ( node.id=my.node_id
                 AND node.version=my.version
                 AND lower(my.metadata_type)='os_y' )
          INNER JOIN metadata as mlat
            ON ( node.id=mlat.node_id
                 AND node.version=mlat.version
                 AND lower(mlat.metadata_type)='latitude' )
          INNER JOIN metadata as mlong
            ON ( node.id=mlong.node_id
                 AND node.version=mlong.version
                 AND lower(mlong.metadata_type)='longitude' )
          ORDER BY node.name";
    }

    my @cat1stuff;
    my @cat2stuff;
    my $sth = $dbh->prepare( $sql{cat1} );
    $sth->execute( lc( $cat1 ) ) or die $dbh->errstr;
    while ( my ( $id, $name, $x, $y, $lat, $long ) = $sth->fetchrow_array ) {
      my $url = $base_url . "?" . $formatter->node_name_to_node_param( $name );
      push @cat1stuff, { id => $id, name => $name, url => $url,
                         x => $x, y => $y, lat => $lat, long => $long };
    }
    $sth = $dbh->prepare( $sql{cat2} );
    if ( $cat2 ) {
      $sth->execute( lc( $cat2 ) ) or die $dbh->errstr;
    } else {
      $sth->execute or die $dbh->errstr;
    }
    while ( my ( $id, $name, $x, $y, $lat, $long ) = $sth->fetchrow_array ) {
      my $url = $base_url . "?" . $formatter->node_name_to_node_param( $name );
      push @cat2stuff, { id => $id, name => $name, url => $url,
                         x => $x, y => $y, lat => $lat, long => $long };
    }

    if ( $show_map ) {
      %tt_vars = (
                   %tt_vars,
                   exclude_navbar      => 1,
                   enable_gmaps        => 1,
                   display_google_maps => 1,
                   show_map            => 1,
                   lat                 => $config->centre_lat,
                   long                => $config->centre_long,
                   zoom                => $config->default_gmaps_zoom,
                 );
      my ( %origin_results, %end_results );
      foreach my $origin ( @cat1stuff ) {
        foreach my $end ( @cat2stuff ) {
          my $thisdist = int( sqrt(   ( $origin->{x} - $end->{x} )**2
                                    + ( $origin->{y} - $end->{y} )**2
                                  ) + 0.5 );
          if ( $thisdist <= $dist ) {
            $origin_results{ $origin->{name} } = $origin;
            $end_results{ $end->{name} } = $end;
          }
        }
      }

      if ( $q->param( "include_all_origins" ) ) {
        %origin_results = map { $_->{name} => $_ } @cat1stuff;
      }

      my @results;
      foreach my $res ( sort { $a->{name} cmp $b->{name} } values %origin_results ) {
        push @results, { %$res, type => "origin" };
      }
      foreach my $res ( sort { $a->{name} cmp $b->{name} } values %end_results ) {
        push @results, { %$res, type => "end" };
      }

      # I hate that I have to do this.  Hate it, hate it.
      foreach my $res ( @results ) {
        my ( $long, $lat ) = OpenGuides::Utils->get_wgs84_coords(
                                        latitude  => $res->{lat},
                                        longitude => $res->{long},
                                        config    => $config );
        $res->{lat} = $lat;
        $res->{long} = $long;
      }
      $tt_vars{results} = \@results;
    } else {
      my @results;
      foreach my $origin ( @cat1stuff ) {
        my @thisres;
        foreach my $end ( @cat2stuff ) {
          if ( $origin->{name} eq $end->{name} ) {
            next;
          }
          my $thisdist = int( sqrt(   ( $origin->{x} - $end->{x} )**2
                                    + ( $origin->{y} - $end->{y} )**2
                                  ) + 0.5 );
          if ( $thisdist <= $dist ) {
            push @thisres, { origin => $origin, end => $end,
                             dist => $thisdist };
          }
        }
        @thisres = sort { $a->{dist} <=> $b->{dist} } @thisres;
        push @results, @thisres;
      }
      $tt_vars{results} = \@results;
    }

  }
}

%tt_vars = (
             %tt_vars,
             addon_title => "Category Search",
           );

print $q->header;
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH => ".:$custom_template_path:$template_path"  } );
$tt->process( "find.tt", \%tt_vars );

sub setup_form_fields {
  my $any_string = " -- any -- ";
  my @categories = $wiki->list_nodes_by_metadata(
    metadata_type  => "category",
    metadata_value => "category",
    ignore_case    => 1,
  );
  @categories = map { s/^Category //; $_; } @categories;
  @categories = sort( @categories );

  $tt_vars{catbox1} = $q->popup_menu( -name   => "cat1",
                                -values => [ "", @categories ],
                                -labels => { "" => $any_string,
                                             map { $_ => $_ } @categories }
                              );
  $tt_vars{catbox2} = $q->popup_menu( -name   => "cat2",
                                -values => [ "", @categories ],
                                -labels => { "" => $any_string,
                                             map { $_ => $_ } @categories }
                              );
  my $distbox = qq( <input type="text" size="4" maxlength="4" name="distance");
  if ( $q->param( "distance" ) ) {
    $distbox .= "value=\"" . $q->param( "distance" ) . "\"";
  }
  $distbox .= "> metres ";
  $tt_vars{distbox} = $distbox;

  $tt_vars{show_map_box} = $q->checkbox( -name => "show_map",
                                                 -value => 1, label => "" );
  $tt_vars{include_all_origins_box} = $q->checkbox( -name => "include_all_origins",
                                                 -value => 1, label => "" );
}
