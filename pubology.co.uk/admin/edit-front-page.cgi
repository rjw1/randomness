#!/usr/bin/perl -w

use strict;

use lib qw(
            /export/home/pubology/lib/
            /export/home/pubology/perl5/lib/perl5/
          );

use CGI;
use CGI::Carp qw( fatalsToBrowser );
use Template;

my $HOME = "/export/home/pubology";
my $base_dir = "$HOME/web/vhosts/pubology.co.uk/";
my $base_url = "http://pubology.co.uk/";

my $q = CGI->new;
my $cgi_url = $q->url();

# Set up template stuff
my $tt_config = {
  INCLUDE_PATH => "$HOME/templates/",
  OUTPUT_PATH => $base_dir,
};
my $tt = Template->new( $tt_config ) or croak Template->error;

my $errmsg;

my $text = $q->param( "front_page_text" );

if ( $q->param( "Save" ) ) {
  if ( !$text ) {
    $errmsg = "<p>Must supply some text.</p>";
  }
}

if ( $errmsg || !$q->param( "Save" ) ) {
  print_form_and_exit( errmsg => $errmsg );
}

write_index_page();

print $q->header;
print <<EOF;
<!DOCTYPE html>
<html>
<head>
  <title>Pubology pub map &#8212; Front page edited</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <link rel="stylesheet" href="http://the.earth.li/~kake/tmp/ewan/styles.css" 
   type="text/css" />
</head>
<body>
  <h1 class="page_header">Pubology map</h1>
  <h2>Front page edited</h2>

  <p><a href="$cgi_url">Edit it again</a>.</p>
  <p><a href="../index.html">View it</a>.</p>
</body>
</html>

EOF

sub write_index_page {
  my $tt_vars = {};
  open( my $output_fh, ">", "$base_dir/index.html" )
    || print_form_and_exit( errmsg => $! );
  $tt->process( "index.tt", $tt_vars, $output_fh )
    || print_form_and_exit( errmsg => $tt->error );
}

sub print_form_and_exit {
  my %args = @_;

  my %tt_vars = (
                  cgi_url => $cgi_url,
                  front_page_text_field => $q->textarea(
                      -name => "front_page_text",
                      -rows => 20,
                      -columns => 100,
                  ),
                  errmsg => $args{errmsg} || "",
                );
  print $q->header;
  $tt->process( "edit_front_page_form.tt", \%tt_vars ) || die $tt->error;
  exit 0;
}
