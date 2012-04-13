package PubSite::Pub;
use strict;

use Flickr::API2;
use Geo::Coordinates::OSGB qw( grid_to_ll );
use Geo::Coordinates::OSTN02 qw( OSGB36_to_ETRS89 ETRS89_to_OSGB36 );

use base qw( Class::Accessor );
PubSite::Pub->mk_accessors( qw( id name closed demolished alt_name date_built
                         date_closed
                         addr_num addr_street postcode former_addr owner
                         os_x os_y location_accurate website rgl fap_rating fap
                         pubs_galore bite
                         bite_2 qype dead_pubs london_eating time_out_rating
                         time_out other_link other_link_2 other_link_3
                         gbg notes flickr ) );

=head1 NAME

PubSite::Pub - Model a single pub for Ewan's pub site.

=head1 DESCRIPTION

Object modelling a single pub.

=head1 METHODS

=over

=item B<new>

  my $pub = PubSite::Pub->new(
    id => 12345,
    name => "Red Lion",
    closed => 1,
    demolished => 0,
    alt_name => "Red Dragon",
    date_built => 1905,
    date_closed => 1980,
    addr_num => 5,
    addr_street => "High Street",
    postcode => "SE1 1ES",
    former_addr => "5 High Street North",
    owner => "Mitchells and Butlers",
    os_x => 532281,
    os_y => 179972,
    location_accurate => 1,
    website => "http://red-lion.info",
    rgl => "http://london.randomness.org.uk/wiki.cgi?Red_Lion,_SE1_1ES",
    fap_rating => 3,
    fap => "http://fancyapint.com/pubs/pub1234.php",
    pubs_galore => "http://www.pubsgalore.co.uk/pubs/12345/",
    bite => "http://www.beerintheevening.com/pubs/s/12/12345/", 
    bite_2 => "",
    qype => "http://www.qype.co.uk/place/1234567",
    dead_pubs => "",
    london_eating => "",
    time_out_rating => 3,
    time_out => "",
    other_link => "http://mypubsite.com/red-lion",
    other_link_2 => "http://anotherpubsite.com/red-lion",
    other_link_3 => "http://yetanotherpubsite.com/red-lion",
    gbg => "2008, 2009, 2012",
    notes => "This pub is an imaginary one.",
    flickr => "http://www.flickr.com/photos/55935853@N00/1234567890/",
    photo_url => "http://farm7.static.flickr.com/123456.jpg",
    photo_width => 500,
    photo_height => 320,
  );

=cut

sub new {
  my ( $class, %args ) = @_;
  my $self = \%args;
  bless $self, $class;
  return $self;
}

=item B<lat_and_long>

Returns an array containing the pub's latitude and longitude,
calculated from the stored values of os_x and os_y.  If os_x or os_y
is missing, returns undef.

=cut

sub lat_and_long {
  my $self = shift;
  my $x = $self->os_x;
  my $y = $self->os_y;

  if ( !$x || !$y ) {
    return undef;
  }

  ( $x, $y ) = OSGB36_to_ETRS89( $x, $y );
  my ( $lat, $long ) = grid_to_ll($x, $y, "WGS84");
  return ( $lat, $long );
}

=item B<lat>

Returns the pub's latitude, calculated from the stored values of os_x
and os_y.  If os_x or os_y is missing, returns undef.

=cut

sub lat {
  my $self = shift;
  my ( $lat, $long ) = $self->lat_and_long;
  return $lat;
}

=item B<long>

Returns the pub's longitude, calculated from the stored values of os_x
and os_y.  If os_x or os_y is missing, returns undef.

=cut

sub long {
  my $self = shift;
  my ( $lat, $long ) = $self->lat_and_long;
  return $long;
}

=item B<not_on_map>

Returns true if and only if either os_x or os_y is missing.

=cut

sub not_on_map {
  my $self = shift;
  if ( $self->os_x && $self->os_y ) {
    return 0;
  }
  return 1;
}

=item B<address>

  my $address = $pub->address;

Returns a nicely-formatted address constructed from addr_num, addr_street,
and postcode.

=cut

sub address {
  my $self = shift;
  my $address = $self->addr_num ? $self->addr_num . " " : "";
  $address .= $self->addr_street . ", " . $self->postcode;
  return $address;
}

=item B<has_links>

  my $boolean = $pub->has_links;

Returns true if and only if the pub has at least one associated link, e.g.
RGL, BITE, etc.

=cut

sub has_links {
  my $self = shift;
  foreach my $key ( qw( rgl fap bite qype dead_pubs pubs_galore other_link
                        other_link_2 ) ) {
    if ( $self->{$key} ) {
      return 1;
    }
  }
  return 0;
}

=item B<Other accessors>

You can access any of the things you put in when you called new(), e.g.

  my $notes = $pub->notes;

=back

=cut

sub TO_JSON {
  my $self = shift;
  return {
    id => $self->id,
    name => $self->name,
    lat => $self->lat,
    long => $self->long,
    not_on_map => $self->not_on_map,
    address => $self->address,
    demolished => $self->demolished,
    closed => $self->closed,
  };
}

1;
