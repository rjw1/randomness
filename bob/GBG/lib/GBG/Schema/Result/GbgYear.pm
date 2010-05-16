package GBG::Schema::Result::GbgYear;

use strict;
use warnings;

use base 'DBIx::Class';

__PACKAGE__->load_components("InflateColumn::DateTime", "Core");
__PACKAGE__->table("gbg_year");
__PACKAGE__->add_columns(
  "pub_id",
  { data_type => "integer", default_value => undef, is_nullable => 1, size => 4 },
  "year_id",
  { data_type => "integer", default_value => undef, is_nullable => 1, size => 4 },
);
__PACKAGE__->belongs_to("pub_id", "GBG::Schema::Result::Pub", { id => "pub_id" });
__PACKAGE__->belongs_to("year_id", "GBG::Schema::Result::Year", { id => "year_id" });


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2009-09-22 00:39:38
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:6P3OElQFqXUiv/2ADIhjYw


# You can replace this text with custom content, and it will be preserved on regeneration
1;
