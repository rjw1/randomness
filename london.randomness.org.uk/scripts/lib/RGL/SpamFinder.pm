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

    if ( $content =~ /\b(viagra|cialis|supermeganah|tramadol|vicodin|phentermine|buyphentermine|adipex|phendimetrazine|ephedrine|lipitor|hydrocodone|replica-watches|propecia|ativan|levitra|lexapro|ambien|citalopram|effexor|fluoxetine|prozac|kamagra|accutane|zithromax|clenbuterol|nolvadex|lorazepam|clonazepam|diazepam|valium|clomid|rimonabant|xenical|lolita|lolitas)\b/is ) {
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

       if ( $name eq "Thattukada, E12 6SJ"
              && $comment =~ m|\w{20},\s+http://| ) {
            $class->notify_admins( %args, id => "00036",
                                   reason => "20 char + URL comment on $name" );
            return 1;
        }

       if ( $name eq "Hackney Empire, E8 1EJ"
              && $comment =~ m|\w{20},\s+<a\s+href="http.*</a>| ) {
            $class->notify_admins( %args, id => "00037",
                                   reason => "20 char + URL comment on $name" );
            return 1;
        }

        if ( $username =~ /^[a-z]+\s[a-z]+$/ ) {
            my $text = "$username $comment";
            if ( $text =~ /q[a-tv-z].*q[a-tv-z]/ ) {
                $class->notify_admins( %args, id => "00038",
       reason => "two-word lowercase username + two occurrences of q+non-u" );
                return 1;
            }
        }

        if ( $content =~ 'http://' && $content =~ /\bxanax\b/ ) {
            $class->notify_admins( %args, id => "00040",
                                   reason => "'xanax' + URL" );
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
