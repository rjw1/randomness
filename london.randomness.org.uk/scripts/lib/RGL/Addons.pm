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
                  common_categories => $config->enable_common_categories,
                  common_locales => $config->enable_common_locales,
                  catloc_link => $config->script_url
                                 . $config->script_name . "?id=",
                  formatting_rules_link => $config->formatting_rules_link,
                  formatting_rules_node => $config->formatting_rules_node,
                  not_editable => 1,
                );

  return %tt_vars;
}

1;
