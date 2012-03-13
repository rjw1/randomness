#!/usr/bin/perl

use strict;
use warnings;

use lib qw( /export/home/rgl/web/vhosts/london.randomness.org.uk/scripts/lib/ );
use lib qw( /export/home/rgl/perl5/lib/perl5 );

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use DateTime;
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

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;

my $dbh = $wiki->store->dbh;

my ($min_date, $max_date);

if ( $config->dbtype eq "mysql" ) {
  $min_date = "current_date() - interval 1 month
                         - interval dayofmonth(now() - interval 1 month) day
                         + interval 1 day";
  $max_date = "current_date() - interval dayofmonth(now()) day";
} else {
  $min_date = "date_trunc( 'month', current_date ) - interval '1 month'";
  $max_date = "date_trunc( 'month', current_date)";
}

my %sql = (
  edit_count     => "
    SELECT count(*)
    FROM content
                    ",
  username_count => "
    SELECT count(distinct lower(metadata_value))
    FROM metadata
    WHERE metadata_type='username'
                    ",
  month_edit_count => "
    SELECT count(*)
    FROM content
    WHERE modified >= $min_date
      AND modified < $max_date
                      ",
  month_username_count => "
    SELECT count( distinct lower(metadata_value) )
    FROM metadata
      INNER JOIN content ON content.node_id=metadata.node_id
                      AND content.version=metadata.version
    WHERE modified >= $min_date
      AND modified < $max_date
      AND metadata_type='username'
                          ",
  month_image_count => "
    SELECT count(*)
    FROM ( SELECT content.node_id, min(content.modified) AS date_added
           FROM content
             INNER JOIN metadata ON content.node_id=metadata.node_id
                                 AND content.version=metadata.version
           WHERE metadata.metadata_type='node_image'
           GROUP BY content.node_id
         ) AS img
    WHERE img.date_added >= $min_date
      AND img.date_added < $max_date
                       ",
);

my %data;
foreach my $query ( keys %sql ) {
    my $sth = $dbh->prepare( $sql{$query} );
    $sth->execute or die $dbh->errstr;
    my ( $n ) = $sth->fetchrow_array;
    $data{$query} = $n;
}

$data{real_count}  = RGL::Addons->get_page_count( wiki => $wiki,
                                                  ignore_categories => 1,
                                                  ignore_locales => 1,
                                                );
$data{total_count} = RGL::Addons->get_page_count( wiki => $wiki );
$data{image_count} = RGL::Addons->get_num_photos( wiki => $wiki );

$data{month_real_count}  = RGL::Addons->get_page_count( wiki => $wiki,
                                                  ignore_categories => 1,
                                                  ignore_locales => 1,
                                                  added_last_month => 1,
                                                );
$data{month_total_count} = RGL::Addons->get_page_count( wiki => $wiki,
                                                  added_last_month => 1,
                                                );

$tt_vars{data} = \%data;

# Get the month.
my $dt = DateTime->now;
$dt->subtract( months => 1 );
$tt_vars{last_month_name} = $dt->month_name . " " . $dt->year;

# Do the template stuff
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

$tt_vars{addon_title} = "RGL Statistics";

print $q->header;
$tt->process( "stats.tt", \%tt_vars ) or die $tt->error;
