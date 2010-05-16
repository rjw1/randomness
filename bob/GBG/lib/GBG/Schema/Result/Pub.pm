package GBG::Schema::Result::Pub;

use strict;
use warnings;

use base 'DBIx::Class';

__PACKAGE__->load_components("InflateColumn::DateTime", "Core");
__PACKAGE__->table("pub");
__PACKAGE__->add_columns(
  "id",
  {
    data_type => "integer",
    default_value => "nextval('pub_serial'::regclass)",
    is_nullable => 0,
    size => 4,
  },
  "name",
  {
    data_type => "character varying",
    default_value => undef,
    is_nullable => 1,
    size => 255,
  },
  "visited",
  {
    data_type => "boolean",
    default_value => "false",
    is_nullable => 1,
    size => 1,
  },
);
__PACKAGE__->set_primary_key("id");
__PACKAGE__->add_unique_constraint("pubid", ["id"]);
__PACKAGE__->add_unique_constraint("pub_pkey", ["id"]);
__PACKAGE__->has_many(
  "gbg_years",
  "GBG::Schema::Result::GbgYear",
  { "foreign.pub_id" => "self.id" },
);


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2009-09-22 00:39:38
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:UdD6Y7QZpwKEUtxlPZ5nGA


# You can replace this text with custom content, and it will be preserved on regeneration
sub year_count {
        my ($self) = @_;
    
        # Use the 'many_to_many' relationship to fetch all of the authors for the current
        # and the 'count' method in DBIx::Class::ResultSet to get a SQL COUNT
        return $self->gbg_years->count;
    }
1;
