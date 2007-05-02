package RGL::Addons;

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

  return %tt_vars;
}

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

  my $any_string = " -- any -- ";
  my $box = $q->popup_menu( -name   => "tube",
                            -values => [ "", @tubes ],
                            -labels => { "" => $any_string,
                                         map { $_ => $_ } @tubes },
                           );

  return $box;
}

1;
