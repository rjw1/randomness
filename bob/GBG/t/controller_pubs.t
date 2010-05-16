use strict;
use warnings;
use Test::More tests => 3;

BEGIN { use_ok 'Catalyst::Test', 'GBG' }
BEGIN { use_ok 'GBG::Controller::pubs' }

ok( request('/pubs')->is_success, 'Request should succeed' );


