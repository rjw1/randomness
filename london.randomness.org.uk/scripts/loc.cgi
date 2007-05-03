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
my $locator = Wiki::Toolkit::Plugin::Locator::Grid->new( x => "os_x", y => "os_y" );
$wiki->register_plugin( plugin => $locator );
my $formatter = $wiki->formatter;

my $q = CGI->new;

print $q->header;
my $self_url = $q->url( -relative );

print <<EOHTML;
<head>
  <link rel="stylesheet" href="http://london.randomness.org.uk/stylesheets/london.css"
  type="text/css" />
  <title>Randomness guide Kakesearch</title>
</head>
<body>
  <div id="body_wrapper">
  
  <div id="banner"><h1><a href="http://london.randomness.org.uk/">Randomness Guide to London</a> &#8212; Kakesearch</h1></div>

  <div id="maincontent">
    <div class="see_other_searches">
      See also: <a href="../wiki.cgi?Ways_To_Search_RGL">Ways To Search RGL</a>
    </div>

    <p>Note: not intended for general use, just a little thingy to help me
    figure out locales.  I know the stylesheet doesn't look right on this
    page.  I may fix it one day, but it's not a high priority.</p>
EOHTML

print_form();

if ( $q->param( "do_search" ) ) {
  my $loc = $q->param( "loc" );
  my $dist = $q->param( "distance" );
  my $not_in_locale = $q->param( "notinloc" ) || 0;

  $dist ||= 0;
  $dist =~ s/[^0-9]//g;

  if ( !$dist || !$loc ) {
    print "<p>Must supply both distance and locale.</p>";
  } else {
    my $dbh = $wiki->store->dbh;
    my $sql = "
SELECT node.name
FROM node
INNER JOIN metadata as md
  ON ( node.id=md.node_id
       AND node.version=md.version
       AND lower(md.metadata_type)='locale'
       AND lower(md.metadata_value)=?)
ORDER BY node.name
";

    my $sth = $dbh->prepare( $sql );

    my @in_locale;
    $sth->execute( lc( $loc ) ) or die $dbh->errstr;
    while ( my ( $name ) = $sth->fetchrow_array ) {
      push @in_locale, $name;
    }

    my @results;
    foreach my $origin ( @in_locale ) {
      my @things = $locator->find_within_distance( node   => $origin,
                                                   metres => $dist );
      my @thisres;
      foreach my $end ( @things ) {
        my $thisdist = $locator->distance( from_node => $origin,
                                           to_node   => $end );
        my %node_data = $wiki->retrieve_node( $end );
        my $locs = $node_data{metadata}{locale};
        my %lochash = map { $_ => 1; } @$locs;
        unless ( $not_in_locale && $lochash{$loc} ) {
          push @thisres, { origin => $origin, end => $end, dist => $thisdist,
                           locs => $locs };
        }
      }
      @thisres = sort { $a->{dist} <=> $b->{dist} } @thisres;
      push @results, @thisres;
    }

    if ( @results == 0 ) {
      print "<p>No results, sorry.</p>";
    } else {
      my $base_url = $config->script_url . $config->script_name . "?";
      my $last_origin = "";
      print "<table border=\"1\">\n"
            . "<tr><th><b>In $loc</b></th><th><b>&nbsp;</b></th>"
            . "<th><b>Distance (metres)</b></th></tr>\n";
      foreach my $set ( @results ) {
        my $origin_name = $set->{origin};
        my $end_name = $set->{end};
        my $origin_url = $base_url
                       . $formatter->node_name_to_node_param( $origin_name );
        my $end_url    = $base_url
                       . $formatter->node_name_to_node_param( $end_name );
        print "<tr>\n";
        if ( $last_origin ne $origin_name ) {
          print "<td><a href=\"$origin_url\">$origin_name</a></td>\n";
        } else {
          print "<td>&nbsp;</td>\n";
        }
        print "<td><a href=\"$end_url\">$end_name</a><br />"
              . "<small>Locales: " . join( ", ", @{$set->{locs}} ) . "</small></td>\n"
              . "<td>" . $set->{dist}   . "</td>\n"
              . "</tr>\n";
        $last_origin = $origin_name;
      }
      print "</table>\n";
    }
  }
}

print <<EOHTML;
</div>
</body>
</html>
EOHTML

sub print_form {
  my $not_in_locale = $q->param( "notinloc" ) || 0;
  my $any_string = " -- any -- ";
  my @locales = $wiki->list_nodes_by_metadata(
    metadata_type  => "category",
    metadata_value => "locales",
    ignore_case    => 1,
  );
  @locales = map { s/^Locale //; $_; } @locales;
  @locales = sort( @locales );

  my $locbox = $q->popup_menu( -name   => "loc",
                               -values => [ "", @locales ],
                               -labels => { "" => $any_string,
                                            map { $_ => $_ } @locales }
                             );
  my $distbox = qq( <input type="text" size="4" maxlength="4" name="distance");
  if ( $q->param( "distance" ) ) {
    $distbox .= "value=\"" . $q->param( "distance" ) . "\"";
  }
  $distbox .= "> metres ";
  my $exbox = '<input type="checkbox" name="notinloc" value="1" '
              . ( $not_in_locale ? 'checked="1"' : '' )
              . '/> Exclude things that are themselves in this locale.';
                               

  print <<EOHTML;
    <form action="$self_url" method="GET">
      <p>Find me things within $distbox of things in
      locale $locbox.</p>
      <p><small>$exbox</small></p>
      <input type="hidden" name="do_search" value="1">
      <input type="submit" name="Search" value="Search">
    </form>
EOHTML
}
