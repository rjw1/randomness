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

my $q = CGI->new;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;
my $dbh = $wiki->store->dbh;

my %tt_vars = RGL::Addons->get_tt_vars( config => $config );

my $node_param = $q->param( "id" ) || "";
my $node;
if ( $node_param ) {
    $node = $formatter->node_param_to_node_name( $node_param );
    if ( $node && $wiki->node_exists( $node ) ) {
        $tt_vars{node_name} = $q->escapeHTML( $node );
        $tt_vars{node_param} = $formatter->node_name_to_node_param( $node );
        $tt_vars{addon_title} = "Add a comment to $tt_vars{node_name}";
    }
}

$tt_vars{addon_title} ||= "Add a comment to a page";

# Add the comment if there is one.
my $username = $q->param( "username" );
my $comment = $q->param( "comment" );
if ( $node && $comment ) {
    my %node_data = $wiki->retrieve_node( $node );
    my %new_metadata = OpenGuides::Template->extract_metadata_vars( 
        wiki    => $wiki,
        config  => $config,
        metadata => $node_data{metadata},
    );

    foreach my $param ( qw(coord_field_1 coord_field_1_name coord_field_1_value
                           coord_field_2 coord_field_2_name coord_field_2_value
                           dist_field ) ) {
        delete $new_metadata{$param};
    }

    $new_metadata{opening_hours_text} = $new_metadata{hours_text};

    $comment =~ s/\r\n/\n/gs;
    $username ||= "Anonymous";
    %new_metadata = (
                      %new_metadata,
                      username     => $username,
                      comment      => "Added a comment.",
                      host         => $ENV{REMOTE_ADDR},
                      edit_type    => "Normal edit",
                      major_change => 1,
                    );

    # Don't want blank values in integerifiable fields; OpenGuides::Template
    # ->extract_metadata_vars gives us undef values for these.
    foreach my $param ( qw( osie_x osie_y os_x os_y latitude longitude ) ) {
        if ( !defined $new_metadata{$param} ) {
            delete $new_metadata{$param};
        }
    }

    my $new_content = $node_data{content} . "\r\n\r\n"
                      . "Comment added by $username: $comment";

    my $spam_detector = $config->spam_detector_module; 
    my $is_spam; 
    if ( $spam_detector ) { 
        eval { 
            eval "require $spam_detector"; 
            $is_spam = $spam_detector->looks_like_spam( 
                node    => $node, 
                content => $new_content, 
                metadata => \%new_metadata,
                via_add_comment => 1,
                added_comment => $comment,
            ); 
        }; 
    } 
    
    if ( $is_spam ) { 
        my $output = OpenGuides::Template->output( 
            wiki     => $wiki, 
            config   => $config, 
            template => "spam_detected.tt", 
            vars     => { 
                          not_editable => 1, 
                        }, 
        ); 
        print $output; 
        exit 0;
    }

    my $ok = $wiki->write_node( $node, $new_content, $node_data{checksum},
                                \%new_metadata );

    if ( $ok ) {
        print $guide->redirect_to_node( $node );
        exit 0;
    }

    $tt_vars{commit_error} = 1;
}

# Do the template stuff.
my $custom_template_path = $config->custom_template_path || "";
my $template_path = $config->template_path;
my $tt = Template->new( { INCLUDE_PATH =>
                                   "$custom_template_path:$template_path"  } );

print $q->header;
$tt->process( "add_comment.tt", \%tt_vars );
