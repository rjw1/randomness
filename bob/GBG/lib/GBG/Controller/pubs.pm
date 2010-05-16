package GBG::Controller::pubs;

use strict;
use warnings;
use parent 'Catalyst::Controller';

=head1 NAME

GBG::Controller::pubs - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut


=head2 index

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;
 $c->stash->{pubs} = [$c->model('DB::Pub')->all];
 $c->stash->{template} = 'pubs/index.tt';

}


=head1 AUTHOR

Bob Waker,,,

=head1 LICENSE

This library is free software. You can redistribute it and/or modify
it under the same terms as Perl itself.

=cut

1;
