package GBG::Schema::Result::Year;

use strict;
use warnings;

use base 'DBIx::Class';

__PACKAGE__->load_components("InflateColumn::DateTime", "Core");
__PACKAGE__->table("year");
__PACKAGE__->add_columns(
  "id",
  { data_type => "integer", default_value => undef, is_nullable => 0, size => 4 },
  "name",
  {
    data_type => "character varying",
    default_value => undef,
    is_nullable => 1,
    size => 255,
  },
);
__PACKAGE__->set_primary_key("id");
__PACKAGE__->add_unique_constraint("yearid", ["id"]);
__PACKAGE__->add_unique_constraint("year_pkey", ["id"]);
__PACKAGE__->has_many(
  "gbg_years",
  "GBG::Schema::Result::GbgYear",
  { "foreign.year_id" => "self.id" },
);


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2009-09-22 00:39:38
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:bfggDtqIwUCzGRuS0zvkww


# You can replace this text with custom content, and it will be preserved on regeneration
1;
