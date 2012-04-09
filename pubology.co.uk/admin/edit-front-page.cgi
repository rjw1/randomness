#!/usr/bin/perl -w

use strict;

use lib qw(
            /export/home/pubology/lib/
            /export/home/pubology/perl5/lib/perl5/
          );

use CGI;
use CGI::Carp qw( fatalsToBrowser );
use HTML::Entities;
use HTML::PullParser;
use HTML::TokeParser;
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

write_index_page( text => $text );

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
  my %args = @_;
  my $text = $args{text};
  my $encoded_text = "";

  # deal with line breaks
#  $text =~ s|\r\n|<br>|g;

  # PullParser rather than TokeParser because it seems a simpler way of doing
  # it here.  I think?  This may be an artefact of me having previously done
  # it this way in Wiki::Toolkit though.
  my $parser = HTML::PullParser->new(
                                      doc => $text,
                                      start => '"TAG", tag, text',
                                      end   => '"TAG", tag, text',
                                      text  => '"TEXT", tag, text'
                                    );

  my %allowed = map { lc($_) => 1, "/" . lc($_) => 1 }
                qw( b i strong em a br ul li hr h3 h4 h5 h6 p );
  while ( my $token = $parser->get_token ) {
    my ( $flag, $tag, $stuff, $attr ) = @$token;
    if ( $flag eq "TAG" and !defined $allowed{ lc( $tag ) } ) {
      $encoded_text .= encode_entities( $stuff );
    } else {
      $encoded_text .= $stuff;
    }
  }

  my $tt_vars = { text => $encoded_text };
  open( my $output_fh, ">", "$base_dir/index.html" )
    || print_form_and_exit( errmsg => $! );
  $tt->process( "index.tt", $tt_vars, $output_fh )
    || print_form_and_exit( errmsg => $tt->error );
}

sub print_form_and_exit {
  my %args = @_;

  open( my $fh, "<", "$base_dir/index.html" )
    || die $!;
  my $parser = HTML::TokeParser->new( $fh );

  my $current_text = "";
  while ( my $token = $parser->get_tag( "div" ) ) {
    my $attrs = $token->[1];
    if ( $attrs->{id} eq "front_page_text" ) {
      while ( my $bit = $parser->get_token ) {
        if ( $bit->[0] eq "E" && $bit->[1] eq "div" ) {
          last;
        }
        if ( $bit->[0] eq "S" ) {
          if ( $bit->[1] eq "a" ) {
            my $href = $bit->[2]->{href};
            my $name = $bit->[2]->{name};
            my $class = $bit->[2]->{class};
            my $id = $bit->[2]->{id};
            $current_text .= "<" . $bit->[1]
                           . ( $href  ? " href=\"$href\"" : "" )
                           . ( $name  ? " name=\"$name\"" : "" )
                           . ( $class ? " class=\"$class\"" : "" )
                           . ( $id    ? " id=\"$id\"" : "" )
                           . ">";
          } else {
            $current_text .= "<" . $bit->[1] . ">";
          }
        } elsif ( $bit->[0] eq "E" ) {
          $current_text .= "</" . $bit->[1] . ">";
        } elsif ( $bit->[0] eq "T" ) {
          $current_text .= $bit->[1];
        }
      }
      last;
    }
  }

  $current_text = encode_entities( $current_text );

  # put linebreaks back
  $current_text =~ s/&lt;br&gt;/\r\n/g;

  my %tt_vars = (
                  cgi_url => $cgi_url,
                  front_page_text_field => $q->textarea(
                      -name => "front_page_text",
                      -rows => 20,
                      -columns => 100,
                  ),
                  current_text => $current_text,
                  errmsg => $args{errmsg} || "",
                );
  print $q->header;
  $tt->process( "edit_front_page_form.tt", \%tt_vars ) || die $tt->error;
  exit 0;
}
