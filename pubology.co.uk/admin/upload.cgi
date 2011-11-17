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
  if ( $postal_district !~ m/^[bcdehiknrstuw][abcdegmnprtw]?\d\d?[cw]?$/i ) {
    $errmsg .= "<p>Postal district in wrong format &#8212; should "
              . "be one or two letters followed by one or two numbers "
              . "and an optional final letter.</p>";
  }
}

if ( $errmsg || !$q->param( "Upload" ) ) {
  print_form_and_exit( errmsg => $errmsg );
}

# OK, we have data to process.
my $tmpfile = $q->param( "csv" );
my $tmpfile_name = $q->tmpFileName( $tmpfile );

my $config = Config::Tiny->read( "/export/home/pubology/pubology.conf" )
               or croak "Can't read config file: $Config::Tiny::errstr "
                      . "(please report this as a bug)";

my %regexes = (
    "central london"    => qr/^[EW]C\d/i,
    "east london"       => qr/^E\d/i,
    "north london"      => qr/^N\d/i,
    "north-west london" => qr/^NW\d/i,
    "outer london"      => qr/^[BCHTU][ABRW]\d/i,
    "south-west london" => qr/^SW\d/i,
    "south-east london" => qr/^SE\d/i,
    "west london"       => qr/^W\d/i,
);

# Check postal district is valid and figure out which area it's in.
my $this_area;
if ( $type eq "postal_district" ) {
  foreach my $area ( keys %regexes ) {
    if ( $postal_district =~ $regexes{$area} ) {
      $this_area = $area;
      last;
    }
  }

  if ( !$this_area ) {
    $errmsg = "<p>Couldn't match postal district \""
              . $q->escapeHTML( $postal_district ) . "\" to an area of "
              . "London.  If you're sure the postal district is correct, "
              . "please report this as a bug.</p>";
  } elsif ( !$config->{lc($this_area)} ) {
    $errmsg = "<p>Couldn't find config information for postal district "
              . $q->escapeHTML( $postal_district ) . " &#8212; please report "
              . "this as a bug.</p>"
  }

  if ( $errmsg ) {
    print_form_and_exit( errmsg => $errmsg );
  }
}

my $flickr_key    = $config->{_}->{flickr_key}    || "";
my $flickr_secret = $config->{_}->{flickr_secret} || "";

my %data = PubSite->parse_csv(
  file          => $tmpfile_name,
  check_flickr  => 0,
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
  rewrite_index( $this_area );
}

# If we get this far then hopefully we've succeeded.
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
  $tt->process( $template, $tt_vars, $output_fh )
    || print_form_and_exit( errmsg => $tt->error );
}

sub write_map_page {
  my $area_name = $this_area;
  $area_name =~ s/\b(\w)/\u$1/g;
  my $area_file = $this_area;
  $area_file =~ s/\s+/-/g;

  my $tt_vars = {
    pubs => \@pubs,
    base_url => $base_url,
    area_name => $area_name,
    area_file => $area_file,
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

sub rewrite_index {
  my $area = shift;

  # already checked this exists in the config
  my %district_names = %{ $config->{ lc( $area ) } };

  opendir( my $dh, $base_dir . "maps" ) || croak "Can't open $base_dir";
  my @files = grep { /\.html$/ } readdir( $dh );
  @files = grep { $regexes{ $this_area } } @files;
  my %urls = map { my $label = $_;
                   $label =~ s/\.html//;
                   { uc( $label ) => $base_url . "maps/$_" }
                 } @files;

  my @districts = map { my $label = uc( $_ );
                        {
                          label => $label,
                          url   => $urls{$label} || "",
                          name  => $district_names{$label}
                        }
                      } sort { pc_cmp( $a, $b ) } keys %district_names;

  my $area_name = $area;
  $area_name =~ s/\b(\w)/\u$1/g;
  my $area_file = $area;
  $area_file =~ s/\s+/-/g;

  my $tt_vars = {
                  area_name => $area_name,
                  districts => \@districts,
                };

  open( my $output_fh, ">", $base_dir . "indexes/$area_file.html" )
    or print_form_and_exit( errmsg => $! );
  $tt->process( "area_index.tt", $tt_vars, $output_fh )
    or print_form_and_exit( errmsg => $tt->error );
}

sub pc_cmp {
  my ( $pc1a, $pc1b, $pc1c, $pc2a, $pc2b, $pc2c );
  $pc1c = $pc1b = $pc1a = shift;
  $pc2c = $pc2b = $pc2a = shift;

  if ( $pc1c =~ m/^[A-Z]+\d+([A-Z]+$)/ ) {
    $pc1c = $1;
    $pc1a =~ s/^([A-Z]+\d+)[A-Z]+$/$1/;
  } else {
    $pc1c = "";
  }

  if ( $pc2c =~ m/^[A-Z]+\d+([A-Z]+$)/ ) {
    $pc2c = $1;
    $pc2a =~ s/^([A-Z]+\d+)[A-Z]+$/$1/;
  } else {
    $pc2c = "";
  }

  $pc1a =~ s/\d//g;
  $pc2a =~ s/\d//g;
  $pc1b =~ s/[A-Z]//g;
  $pc2b =~ s/[A-Z]//g;

  if ( $pc1a ne $pc2a ) {
    return $pc1a cmp $pc2a;
  }

  if ( $pc1b != $pc2b ) {
    return $pc1b <=> $pc2b;
  }

  if ( $pc1c && $pc2c ) {
    return $pc1c cmp $pc2c;
  }

  if ( $pc1c ) {
    return 1;
  }

  if ( $pc2c ) {
    return -1;
  }

  return 0;
}

sub print_form_and_exit {
  my %args = @_;

  my %tt_vars = (
                  cgi_url => $cgi_url,
                  postal_district_field =>
                                  $q->textfield( -name => "postal_district" ),
                  errmsg => $args{errmsg} || "",
                );
  print $q->header;
  $tt->process( "upload_form.tt", \%tt_vars ) || die $tt->error;
  exit 0;
}
