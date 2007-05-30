package RGL::SpamFinder;

use strict;

use Data::Dumper;
use Email::Send;

sub looks_like_spam {
    my ( $class, %args ) = @_;

    my $content = $args{content};

    if ( $content =~ /\bviagra\b/i ) {
        $class->notify_admins( %args, reason => "Matches viagra" );
        return 1;
    }

    if ( $args{via_add_comment} ) {
        if ( ( $content =~ /good\s+site\.\s+thank/i )
             || ( $content =~ /nice\s+site\.\s+thank/i ) ) {
            if ( $content =~ 'http://' ) {
                $class->notify_admins( %args, reason => "'nice site' + URL" );
            }
        }
    }
}

sub notify_admins {
    my ( $class, %args ) = @_;
    my $message = <<EOM;
From: kake\@earth.li
To: kake\@earth.li, bob\@randomness.org.uk
Subject: Attempted spam edit on RGL

Someone just tried to edit RGL, and I said no because it looked like spam.
Here follows a dump of the details:

EOM
    $message .= Dumper( \%args );

    my $sender = Email::Send->new( { mailer => "SMTP" } );
    $sender->mailer_args( [ Host => "localhost" ] );
    $sender->send( $message );
}

1;
