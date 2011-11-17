#!/usr/bin/perl -w

use strict;

use lib qw(
            /export/home/pubology/lib/
            /export/home/pubology/perl5/lib/perl5/
          );

use CGI;
use CGI::Carp qw( fatalsToBrowser );
use Config::Tiny;
use PubSite;
use Template;

my $version = "version-5";

my $base_dir = "/export/home/pubology/web/vhosts/pubology.co.uk/";
my $base_url = "http://pubology.co.uk/";

my $q = CGI->new;
my $cgi_url = $q->url();

# Set up template stuff
my $tt_config = {
  INCLUDE_PATH => "/export/home/pubology/templates/",
  OUTPUT_PATH => $base_dir,
};
my $tt = Template->new( $tt_config ) or croak Template->error;

my $errmsg = "";
my $type = $q->param( "upload_type" ) || "";

if ( $q->param( "Upload" ) ) {
  if ( $type ne "postal_district" && $type ne "pubs" ) {
    $errmsg .= "<p>Wrong upload type: " . $q->escapeHTML( $type )
                     . "(please report this as a bug).</p>";
  }
  if ( !$q->param( "csv" ) ) {
    $errmsg .= "<p>Must supply a CSV file.</p>";
  }
}

my $postal_district;
if ( $type eq "postal_district" ) {
  $postal_district = $q->param( "postal_district" );
  $postal_district =~ s/\s+//g;
  if ( $postal_district !~ m/^[bcdehiknrstuw][abcdegmnprtw]?\d\d?$/i ) {
    $errmsg .= "<p>Postal district in wrong format &#8212; should "
              . "be one or two letters followed by one or two numbers.</p>";
  }
}

if ( $errmsg || !$q->param( "Upload" ) ) {
  # just print the form and exit
  my %tt_vars = (
                  cgi_url => $cgi_url,
                  postal_district_field =>
                                  $q->textfield( -name => "postal_district" ),
                  errmsg => $errmsg,
                );
  print $q->header;
  $tt->process( "upload_form.tt", \%tt_vars ) || die $tt->error;
  exit 0;
}

# OK, we have data to process.
my $tmpfile = $q->param( "csv" );
my $tmpfile_name = $q->tmpFileName( $tmpfile );

my $config = Config::Tiny->read( "/export/home/pubology/pubology.conf" )
#my $config = Config::Tiny->read( "/home/kake/private/ewan/pubology.conf" )
               or croak "Can't read config file: $Config::Tiny::errstr "
                      . "(please report this as a bug)";
my $flickr_key    = $config->{_}->{flickr_key}    || "";
my $flickr_secret = $config->{_}->{flickr_secret} || "";

my %data = PubSite->parse_csv(
  file          => $tmpfile_name,
  check_flickr  => 1,
  flickr_key    => $flickr_key,
  flickr_secret => $flickr_secret,
);
my @pubs = @{ $data{pubs} };

my ( $min_lat, $max_lat, $min_long, $max_long )
  = @data{ qw( min_lat max_lat min_long max_long ) };

my $map_file = "maps/" . lc( $postal_district ) . ".html";
my $map_url = $base_url . $map_file;

foreach my $pub ( @pubs ) {
  write_pub_page( $pub, $map_url );
}

if ( $type eq "postal_district" ) {
  write_map_page();
  rewrite_index_page();
}

# Success!  I hope.
my $succ_msg;
if ( $type eq "pubs" ) {
  $succ_msg = "Data successfully uploaded.";
} else {
  $succ_msg = "Data successfully uploaded for $postal_district. "
              . "<a href=\"$base_url$map_file\">Here is your map</a>.";
}

my %tt_vars = (
                cgi_url => $cgi_url,
                base_url => $base_url,
                succ_msg => $succ_msg,
              );
print $q->header;
$tt->process( "upload_complete.tt", \%tt_vars ) || die $tt->error;

# subroutines

sub write_pub_page {
  my $pub = shift;
  my $map_url = shift;

  my $tt_vars = { pub => $pub, map_url => $map_url,
                  updated => scalar localtime() };

  my $template = "pub_page.tt";
  open( my $output_fh, ">", "$base_dir/pubs/" . $pub->id . ".html" )
      or die $!;
  $tt->process( $template, $tt_vars, $output_fh ) || die $tt->error;
}

sub write_map_page {
  my $tt_vars = {
    pubs => \@pubs,
    base_url => $base_url,
    min_lat => $min_lat,
    max_lat => $max_lat,
    min_long => $min_long,
    max_long => $max_long,
    centre_lat => ( ( $max_lat + $min_lat ) / 2 ),
    centre_long => ( ( $max_long + $min_long ) / 2 ),
    updated => scalar localtime(),
    postal_district => uc( $postal_district ),
  };

  my $template = "map.tt";
  open( my $output_fh, ">", $base_dir . $map_file ) or die $!;
  $tt->process( $template, $tt_vars, $output_fh );
}

sub rewrite_index_page {
  opendir( my $dh, $base_dir . "maps" ) || croak "Can't open $base_dir";
  my @files = grep { /\.html$/ } readdir( $dh );

  my @maps = map { my $label = $_;
                   $label =~ s/\.html//;
                   { url => $base_url . "maps/$_",
                     label => uc( $label ) }
                 } @files;

  my $tt_vars = { maps => \@maps };

  my $template = "index.tt";
  open( my $output_fh, ">", $base_dir . "index.html" ) or die $!;
  $tt->process( $template, $tt_vars, $output_fh );
}
