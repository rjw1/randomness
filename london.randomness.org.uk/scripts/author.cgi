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
my $author = $q->param( "author" );
$author = lc( $author );
$author =~ s/^\s+//;
$author =~ s/\s+$//;
if ( $author ) {
    my $sql = "
        SELECT DISTINCT node.name
        FROM content
        INNER JOIN node
          ON node.id = content.node_id
        INNER JOIN metadata AS author
          ON ( content.node_id = author.node_id
               AND content.version = author.version
               AND lower( author.metadata_type ) = 'username'
             )
        WHERE lower(btrim(author.metadata_value)) = ?
        ORDER BY node.name";

    my $sth = $dbh->prepare( $sql );
    $sth->execute( $author ) or die $dbh->errstr;

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
    SELECT DISTINCT btrim(author.metadata_value) AS author_name
    FROM content
    INNER JOIN metadata AS author
      ON ( content.node_id = author.node_id
           AND content.version = author.version
           AND lower( author.metadata_type ) = 'username'
         )
    WHERE btrim(author.metadata_value) != ''
      AND btrim(author.metadata_value) != 'Anonymous'
      AND btrim(author.metadata_value) != 'Auto Create'
      AND moderated = true";


my $sth = $dbh->prepare( $sql );
$sth->execute or die $dbh->errstr;

my @authors;
while ( my ( $name ) = $sth->fetchrow_array ) {
    push @authors, $name;
}

my %hash = map { lc($_) => $_ } reverse sort @authors;
@authors = sort { lc($a) cmp lc($b) } values %hash;

my $choose_string = " -- choose one -- ";

$tt_vars{author_box} = $q->popup_menu(
                                       -name => "author",
                                       -values => [ "", @authors ],
                                       -labels => { "" => $choose_string,
                                                    map { $_ => $_ }
                                                          @authors },
                                           );

my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

%tt_vars = (
             %tt_vars,
             addon_title => "Pages edited by specific people",
           );

print $q->header;
$tt->process( "author.tt", \%tt_vars ) or die $tt->error;
