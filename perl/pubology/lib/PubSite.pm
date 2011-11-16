package PubSite;
use strict;

use PubSite::Pub;
use Text::CSV::Simple;

=head1 NAME

PubSite - Makes Ewan's pub site.

=head1 DESCRIPTION

A set of tools for turning Ewan's CSV files into a website.

=head1 METHODS

=over

=item B<parse_csv>

  # If you want to check Flickr for photo URLs/heights/widths, you must
  # supply both key and secret.  If one or both is missing then check_flickr
  # will be set to 0.

  my %data = PubSite->parse_csv(
                                 file          => "datafile.csv",
                                 check_flickr  => 1, # or 0
                                 flickr_key    => "mykey",
                                 flickr_secret => "mysecret",
                               );

Returns a hash:

=over

=item pubs - ref to an array of PubSite::Pub objects;

=item min_lat, max_lat, min_long, max_long - scalars

=back

=cut

sub parse_csv {
  my ( $class, %args )  = @_;

  my $csv = $args{file} || die "No datafile supplied";
  my $check_flickr = $args{check_flickr} || 0;
  my $flickr_key = $args{flickr_key};
  my $flickr_secret = $args{flickr_secret};
  if ( !$flickr_key || !$flickr_secret ) {
    $check_flickr = 0;
  }

  my $parser = Text::CSV::Simple->new({ binary => 1 });
  $parser->field_map( qw/id name closed demolished alt_name date_built
                         date_closed
                         addr_num addr_street postcode former_addr owner
                         os_x os_y location_accurate website rgl fap_rating fap
                         pubs_galore bite
                         bite_2 qype dead_pubs london_eating time_out_rating
                         time_out other_link other_link_2 other_link_3
                         gbg notes flickr/ );
  my @data = $parser->read_file( $csv );
  @data = @data[ 1 .. $#data ]; # strip the headings

  @data = sort { $a->{name} cmp $b->{name} } @data;

  my @pubs;
  my ( $min_lat, $max_lat, $min_long, $max_long );

  foreach my $datum ( @data ) {
    foreach my $key ( qw( closed demolished ) ) {
      if ( $datum->{$key} eq "TRUE" ) {
        $datum->{$key} = 1;
      } else {
        $datum->{$key} = 0;
      }
    }

    if ( $check_flickr && $datum->{flickr} ) {
      my $photo_url = $datum->{flickr};

      my ( $user_id, $photo_id ) =
                          $photo_url =~ m{flickr.com/photos/([\d\@N]+)/(\d+)};

      my $flickr_api = Flickr::API2->new({
                         key    => $flickr_key,
                         secret => $flickr_secret,
                       });
      my $flickr_info = $flickr_api->execute_method(
                        "flickr.photos.getSizes", { photo_id => $photo_id } );
      my @photos = @{ $flickr_info->{sizes}{size} };

      foreach my $photo ( @photos ) {
        if ( $photo->{label} eq "Medium" ) {
          $datum->{photo_url} = $photo->{source};
          $datum->{photo_width} = $photo->{width};
          $datum->{photo_height} = $photo->{height};
        }
      }
    }

    my $pub = PubSite::Pub->new( %$datum );
    push @pubs, $pub;

    if ( $pub->not_on_map ) {
      next;
    }

    my ( $lat, $long ) = $pub->lat_and_long;

    if ( !defined $min_lat ) {
      $min_lat = $max_lat = $lat;
    } elsif ( $lat < $min_lat ) {
      $min_lat = $lat;
    } elsif ( $lat > $max_lat ) {
      $max_lat = $lat;
    }
    if ( !defined $min_long ) {
      $min_long = $max_long = $long;
    } elsif ( $long < $min_long ) {
      $min_long = $long;
    } elsif ( $long > $max_long ) {
      $max_long = $long;
    }
  }

  return (
           pubs => \@pubs,
           min_lat => $min_lat,
           max_lat => $max_lat,
           min_long => $min_long,
           max_long => $max_long,
         );
}

=back

=cut

1;
