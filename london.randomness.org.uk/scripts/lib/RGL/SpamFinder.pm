package RGL::SpamFinder;

use strict;

use Data::Dumper;
use Email::Send;

use vars qw( $VERSION );
$VERSION = '0.01';

sub looks_like_spam {
    my ( $class, %args ) = @_;

    my $name = $args{node};
    my $content = $args{content};
    my $username = $args{metadata}{username};
    my $host = $args{metadata}{host};
    my $comment = $args{added_comment} || "";

    if ( $content =~ /\b(viagra|cialis|supermeganah|tramadol|vicodin|phentermine|buyphentermine|adipex|phendimetrazine|ephedrine|lipitor|hydrocodone|replica-watches|propecia|ativan|levitra|lexapro|ambien|citalopram|effexor|fluoxetine|prozac|kamagra|accutane|zithromax|clenbuterol|nolvadex|lorazepam|clonazepam|diazepam|valium|clomid|rimonabant|xenical|lolita|lolitas|vimax)\b/is ) {
        $class->notify_admins( %args, id => "00002", reason => "Matches $1" );
        return 1;
    }

    my @cats = @{ $args{metadata}{category} };
    foreach my $cat ( @cats ) {
        if ( $cat =~ m'http://'i ) {
            $class->notify_admins( %args, id => "00004",
                                   reason => "URL in category field" );
            return 1;
        }
        if ( $cat =~ m/!/ ) {
            $class->notify_admins( %args, id => "00005",
                                   reason => "exclamation mark in category field" );
            return 1;
        }
    }

    my @locs = @{ $args{metadata}{locale} };
    if ( ( scalar @cats == 1 ) && ( scalar @locs == 1 )
         && $cats[0] eq $locs[0] ) {
        $class->notify_admins( %args, id => "00006",
                               reason => "category and locale identical" );
        return 1;
    }

    # Everything below here only matches if we come via "Add a comment".
    if ( $args{via_add_comment} ) {

        if ( ( $comment =~ /http:\/\/.*http:\/\/.*http:\/\//s )
             || ( $comment =~ /https:\/\/.*https:\/\/.*https:\/\//s )
             || ( $comment =~ /a\s+href=.*a\s+href=.*a\s+href=/s ) ) {
            $class->notify_admins( %args, id => "00034",
                              reason => "comment with more than two URLs in" );
            return 1;
        }

        if ( $comment =~ m|\w{6}\s+<a\s+href="http://[a-z]{12}\.com| ) {
            $class->notify_admins( %args, id => "00035",
                    reason => "six-character comment plus link to 12-character URL" );
            return 1;
        }

       if ( $name eq "Arcola Theatre"
              && $comment =~ m|^\w{11},\s+<a\s+href="http://.*\w{10}</a>| ) {
            $class->notify_admins( %args, id => "00039",
                                   reason => "11 char + URL comment on $name" );
            return 1;
        }

       if ( $name eq "Hawksmoor, E1 6BJ"
              && $comment =~ m|^\w{11},\s+<a\s+href="http://.*</a>| ) {
            $class->notify_admins( %args, id => "00040",
                                   reason => "11 char + URL comment on $name" );
            return 1;
        }


       if ( $name eq "Old Salt Quay, SE16 5QU"
              && $comment =~ m|<a\s+href="\s*http://.*</a>| ) {
            $class->notify_admins( %args, id => "00041",
                                   reason => "URL comment on $name" );
            return 1;
        }

    }
}

sub notify_admins {
    my ( $class, %args ) = @_;
    my $datestamp = localtime( time() );
    $args{id} ||= "(none)";
    my $message = <<EOM;
From: kake\@earth.li
To: kake\@earth.li, bob\@randomness.org.uk
Date: $datestamp
Subject: Attempted spam edit on RGL

Someone just tried to edit RGL, and I said no because it looked like spam.
Here follows a dump of the details:

Reason: $args{reason}
ID: $args{id}

EOM
    $message .= Dumper( \%args );

    my $sender = Email::Send->new( { mailer => "SMTP" } );
    $sender->mailer_args( [ Host => "localhost" ] );
    $sender->send( $message );
}

1;
