#!/opt/csw/bin/perl

use strict;
use warnings;

use lib "lib";

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use RGL::Addons;
use OpenGuides::Config;
use OpenGuides::Utils;
use Template;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;
my $base_url = $config->script_url . $config->script_name . "?";

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $q = CGI->new;
my $dbh = $wiki->store->dbh;

# Do search if we have the param.
my $copyright = $q->param( "copyright" );
if ( $copyright ) {
    my $sql = "
        SELECT DISTINCT node.name
        FROM node
        INNER JOIN metadata as copyright
          ON ( node.id = copyright.node_id
               AND node.version = copyright.version
               AND lower( copyright.metadata_type ) = 'node_image_copyright'
             )
        WHERE copyright.metadata_value = ?
        ORDER BY node.name";

    my $sth = $dbh->prepare( $sql );
    $sth->execute( $copyright ) or die $dbh->errstr;

    my @nodes;
    while ( my ( $name ) = $sth->fetchrow_array ) {
        my $param = $formatter->node_name_to_node_param( $name );
        push @nodes, {
                       name => CGI->escapeHTML( $name ),
                       url  => $base_url . $param,
                     };
    }
    $tt_vars{nodes} = \@nodes;
    $tt_vars{searching} = 1;
}

my $sql = "
    SELECT DISTINCT copyright.metadata_value
    FROM node
    INNER JOIN metadata as copyright
      ON ( node.id = copyright.node_id
           AND node.version = copyright.version
           AND lower( copyright.metadata_type ) = 'node_image_copyright'
         )
    ORDER BY copyright.metadata_value";

my $sth = $dbh->prepare( $sql );
$sth->execute or die $dbh->errstr;

my @photographers;
while ( my ( $name ) = $sth->fetchrow_array ) {
    push @photographers, $name;
}

my $any_string = " -- choose one -- ";

$tt_vars{photographer_box} = $q->popup_menu(
                                       -name => "copyright",
                                       -values => [ "", @photographers ],
                                       -labels => { "" => $any_string,
                                                    map { $_ => $_ }
                                                          @photographers },
                                           );

my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

%tt_vars = (
             %tt_vars,
             addon_title => "Pages with photos by specific people",
           );

print $q->header;
$tt->process( "photo_copyright.tt", \%tt_vars ) or die $tt->error;
