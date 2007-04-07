#!/opt/csw/bin/perl

use strict;
use warnings;

use CGI qw( :standard );
use CGI::Carp qw( fatalsToBrowser );
use OpenGuides;
use OpenGuides::Config;
use Wiki::Toolkit::Plugin::Locator::Grid;

my $config_file = $ENV{OPENGUIDES_CONFIG_FILE} || "../wiki.conf";
my $config = OpenGuides::Config->new( file => $config_file );

my $guide = OpenGuides->new( config => $config );
my $wiki = $guide->wiki;
my $formatter = $wiki->formatter;

my $q = CGI->new;

print $q->header;
my $self_url = $q->url( -relative );

print <<EOHTML;
<head>
  <link rel="stylesheet" href="http://london.randomness.org.uk/london.css"
  type="text/css" />
  <title>Randomness Guide to London &#8212; Good Beer Guide pubs with no node image</title>
</head>
<body>
  <h1 id="header"><a href="http://london.randomness.org.uk/">Randomness Guide to London</a> &#8212; <a href="http://london.randomness.org.uk/wiki.cgi?Category_Good_Beer_Guide">Good Beer Guide pubs</a> with no node image</h1>
  <div id="content">
EOHTML

my $locale = $q->param( "locale" );

my $dbh = $wiki->store->dbh;
my $sql = "
SELECT node.name, ml.metadata_value FROM node
INNER JOIN metadata as mgbg
  ON ( node.id=mgbg.node_id
       AND node.version=mgbg.version
       AND lower(mgbg.metadata_type) = 'category'
       AND lower(mgbg.metadata_value) = 'good beer guide'
     )
INNER JOIN metadata as ml
  ON ( node.id = ml.node_id
       AND node.version = ml.version
       AND lower(ml.metadata_type) = 'locale'
     )
";

my $sth = $dbh->prepare( $sql );
$sth->execute or die $dbh->errstr;

my %data;
my %locales;
while ( my ( $name, $this_locale ) = $sth->fetchrow_array ) {
  $locales{$this_locale} = 1;
  if ( $locale && ( lc( $this_locale ) ne lc( $locale ) ) ) {
    next;
  }
  if ( $data{$name} ) {
    push @{$data{$name}}, $this_locale;
  } else {
    $data{$name} = [ $this_locale ];
  }
}

print_form( keys %locales );

my @pubs = keys %data;
@pubs = sort @pubs;

my @lacking;
foreach my $pub ( @pubs ) {
  my %data = $wiki->retrieve_node( $pub );
  if ( !$data{metadata}{node_image} ) {
    push @lacking, $pub;
  }
}

print "<p>Total count: " . scalar @lacking . " of " . scalar @pubs . "</p>\n";

print "<ul>\n";
my $base_url = $config->script_url . $config->script_name . "?";
foreach my $pub ( @lacking ) {
  my $url = $base_url . $formatter->node_name_to_node_param( $pub );
  print "<li><a href=\"$url\">" . CGI->escapeHTML( $pub ) . "</a></li>\n";
}

print <<EOHTML;
</ul>
</body>
</html>
EOHTML

sub print_form {
  my @locales = @_;
  my $any_string = " -- any -- ";
  @locales = map { s/^Locale //; $_; } @locales;
  @locales = sort( @locales );

  my $locbox = $q->popup_menu( -name   => "locale",
                               -values => [ "", @locales ],
                               -labels => { "" => $any_string,
                                            map { $_ => $_ } @locales }
                             );
  print <<EOHTML;
    <form action="$self_url" method="GET">
      <p>Restrict results to locale $locbox <small>(Locales not listed have no pubs with missing images.)</small></p>
      <input type="submit" name="Search" value="Search">
    </form>
EOHTML
}

