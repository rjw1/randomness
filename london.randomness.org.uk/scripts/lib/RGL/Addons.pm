package RGL::Addons;

use OpenGuides::CGI;

=head1 NAME

RGL::Addons - Addons to OpenGuides for the Randomness Guide to London.

=head1 DESCRIPTION

Helpers for the Randomness Guide to London's extra addon scripts.

=head1 METHODS

=over

=item B<get_tt_vars>

Returns a hash of variables for passing to TT; stylesheet, language,
site_name, script_url, site_url, etc.  not_editable is always set to 1.

=cut

sub get_tt_vars {
  my ( $self, %args ) = @_;

  my $config = $args{config};
  my %tt_vars = (
                  stylesheet => $config->stylesheet_url,
                  language   => $config->default_language,
                  site_name  => $config->site_name,
                  script_url => $config->script_url,
                  site_url   => $config->script_url . $config->script_name,
                  full_cgi_url => $config->script_url . $config->script_name,
                  home_link => $config->script_url. $config->script_name,
                  common_categories => $config->enable_common_categories,
                  common_locales => $config->enable_common_locales,
                  catloc_link => $config->script_url
                                 . $config->script_name . "?id=",
                  formatting_rules_link => $config->formatting_rules_link,
                  formatting_rules_node => $config->formatting_rules_node,
                  gmaps_api_key => $config->gmaps_api_key,
                  not_editable => 1,
                );

  my %cookie_data = OpenGuides::CGI->get_prefs_from_cookie(config=>$config); 
  $tt_vars{username} = $cookie_data{username};

  return %tt_vars;
}

=item B<get_nodes_with_geodata>

  my @nodes = RGL::Addons->get_nodes_with_geodata( wiki => $wiki,
                                                   config => $config );

Find all nodes which have geodata set (x and y plus lat and long).
x and y may be OS coords, or UTM eastings and northings.
Returns an array of hashrefs.  Each hashref currently only contains one
key/value pair; the key is C<name> and the value is the name of the node.

=cut

sub get_nodes_with_geodata {
  my ( $class, %args ) = @_;

  my $wiki = $args{wiki};
  my $config = $args{config};
  my $geo_handler = $config->geo_handler;
  my ( $x_name, $y_name );

  if ( $geo_handler == 1 ) {
      $x_name = "os_x";
      $y_name = "os_y";
  } elsif ( $geo_handler == 3 ) {
      $x_name = "easting";
      $y_name = "northing";
  }

  my $dbh = $wiki->store->dbh;
  my $sql = "
    SELECT node.name
    FROM node
    INNER JOIN metadata as mx
      ON ( node.id=mx.node_id
           AND node.version=mx.version
           AND lower(mx.metadata_type)='$x_name' )
    INNER JOIN metadata as my
      ON ( node.id=my.node_id
           AND node.version=my.version
           AND lower(my.metadata_type)='$y_name' )
    INNER JOIN metadata as mlat
      ON ( node.id=mlat.node_id
           AND node.version=mlat.version
           AND lower(mlat.metadata_type)='latitude' )
    INNER JOIN metadata as mlong
      ON ( node.id=mlong.node_id
           AND node.version=mlong.version
           AND lower(mlong.metadata_type)='longitude' )
    ORDER BY node.name";

  my $sth = $dbh->prepare( $sql );
  $sth->execute or die $dbh->errstr;

  my @nodes;
  while ( my ( $name ) = $sth->fetchrow_array ) {
    push @nodes, { name => $name };
  }
  return @nodes;
}

=item B<get_tube_dropdown>

Returns HTML for a dropdown box containing all Tube stations.  Takes no
account of Temporarily Closed.

=cut

sub get_tube_dropdown {
  my ( $self, %args ) = @_;

  my $q = $args{q};
  my $guide = $args{guide};
  my $dbh = $guide->wiki->store->dbh;

  my $sql = "SELECT node.name FROM node
INNER JOIN metadata as tube
  ON ( node.id = tube.node_id AND node.version = tube.version
       AND lower( tube.metadata_type ) = 'category'
       AND lower( tube.metadata_value ) = 'tube'
       AND node.name NOT LIKE 'Category%'
     )
  ORDER BY node.name
";

  my $sth = $dbh->prepare( $sql );
  $sth->execute or die $dbh->errstr;

  my @tubes;
  while ( my ( $tube ) = $sth->fetchrow_array ) {
    push @tubes, $tube;
  }

  my $box = $q->popup_menu( -name   => "tube",
                            -values => [ "", @tubes ],
                            -labels => { "" => "",
                                         map { $_ => $_ } @tubes },
                           );

  return $box;
}

=item B<get_photo_count>

  my $num = RGL::Addons->get_photo_count( wiki => $wiki );

Returns the number of pages that have photos.

=cut

sub get_num_photos {
  my ( $self, %args ) = @_;
  my $wiki = $args{wiki};

  my $dbh = $wiki->store->dbh;
  my $sql = "
    SELECT count(*)
    FROM node
    INNER JOIN metadata as mp
      ON node.id = mp.node_id
        AND node.version = mp.version
        AND mp.metadata_type = 'node_image'
  ";

  my $sth = $dbh->prepare( $sql );
  $sth->execute;

  my ( $count ) = $sth->fetchrow_array;

  return $count;
}

=back

=cut

1;
