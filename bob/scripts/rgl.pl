#!/usr/bin/perl -w

use strict;
use URI;
use URI::QueryParam;
use WWW::Mechanize;
use YAML::Syck;
use Getopt::Long;

my $default_username = "Robobob";
my $default_comment = "an automated bulk upload";
my $datafile = "rgldata";

my $new_page_url = "http://morerandomness.org.uk/openguides/newpage.cgi";
GetOptions ("username=s" => \$default_username,
			"comment=s" => \$default_comment,
			"url=s" => \$new_page_url,
			"file=s" => \$datafile);

if ( $new_page_url ne "http://morerandomness.org.uk/openguides/newpage.cgi" ) {
  print "***** WARNING ***** You seem not to be running on the test guide.\n";
}

open FILE, $datafile or die "Can't open $datafile: $!";
my $datastr;
while (<FILE>) {
  $datastr .= $_;
}
close FILE;

print "Finished reading in data.\n";

my @data = Load( $datastr );

print "Finished processing YAML.\n";

if ( scalar @data ) {
  print scalar( @data ) . " records found.\n";
} else {
  print "Error: no records found.  Exiting.\n";
  exit 0;
}

my $created = 0;
my $skipped = 0;

foreach my $datum ( @data ) {
  if ( !$datum ) {
    print "Warning: blank datum.\n";
    next;
  }
  if ( !$datum->{pagename} ) {
    print "Error: blank pagename.  Exiting.\n";
    exit 0;
  }
  my $pagename = $datum->{pagename};
  print "Checking for existence of $pagename...\n";
  if ( page_exists( $pagename ) ) {
    print "$pagename already exists; skipping.\n";
    $skipped++;
  } else {
    print "$pagename not found; creating it...\n";
    makepage( %$datum );
    $created++;
  }
}

print "$skipped " . ( $skipped == 1 ? "datum" : "data" )
      . " skipped, $created " . ( $created == 1 ? "page" : "pages" )
      . " created.\n";

sub page_exists {
  my $pagename = shift;
  my $agent = WWW::Mechanize->new();
  $agent->get( $new_page_url );
  $agent->submit_form(
                       form_number => 2,
                       fields      => {
                                        pagename => $pagename,
                                      },
                     );
  $agent->follow_link( text => "cancel edit" );
  my $html = $agent->content();
  if ( $html =~ /We don't have a page called/ ) {
#  if ( $html =~ /We don't have a node called/ ) {
    return 0;
  }
  return 1;
}

sub makepage {
  my %args = @_;
  my $pagename = delete $args{pagename};

  my @splitcats = split( /, */, $args{categories} );
  $args{categories} = join( "\r\n", @splitcats );

  my @splitlocs = split( /, */, $args{locales} );
  $args{locales} = join( "\r\n", @splitlocs );

  $args{content} = $args{summary};
  if ( $args{extra_content} ) {
    $args{content} .= "\r\n\r\n" . $args{extra_content};
  }
  delete $args{extra_content};

  my $username = $args{username} || $default_username;
  my $comment  = $args{comment}  || $default_comment;

  my $u = URI->new( $args{map_link} );
  $args{os_x} = $u->query_param( "x" ) || $u->query_param( "X" );
  $args{os_y} = $u->query_param( "y" ) || $u->query_param( "Y" );

  my $agent = WWW::Mechanize->new();
  $agent->get( $new_page_url );
  $agent->submit_form(
                       form_number => 2,
                       fields      => {
                                        pagename => $pagename,
                                      },
                     );
  $agent->submit_form(
                       form_number => 1,
                       fields      => {
                                        %args,
                                        username => $username,
                                        comment => $comment,
                                        edit_type => "Normal edit",
                                      },
                       button => "Save",
                     );
  print "Processed $pagename\n";
  return;
}
