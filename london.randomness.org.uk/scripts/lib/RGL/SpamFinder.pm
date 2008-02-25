package RGL::SpamFinder;

use strict;

use Data::Dumper;
use Email::Send;

sub looks_like_spam {
    my ( $class, %args ) = @_;

    if ( $args{metadata}{comment} =~ /some grammatical corrections/i ) {
        $class->notify_admins( %args,
                               reason => "'some grammatical corrections'" );
        return 1;
    }

    my $name = $args{node};
    my $content = $args{content};
    my $username = $args{metadata}{username};
    my $host = $args{metadata}{host};

    if ( $content =~ /\b(viagra|cialis|supermeganah|tramadol|vicodin|phentermine)\b/is ) {
        $class->notify_admins( %args, reason => "Matches $1" );
        return 1;
    }

    if ( $args{metadata}{comment} =~ /http:\/\/.*http:\/\//s ) {
        $class->notify_admins( %args, reason => "URLs in change comment" );
        return 1;
    }

    my @cats = @{ $args{metadata}{category} };
    foreach my $cat ( @cats ) {
        if ( $cat =~ m'http://'i ) {
            $class->notify_admins( %args, reason => "URL in category field" );
            return 1;
        }
        if ( $cat =~ m'\n'i ) {
            $class->notify_admins( %args,
                                   reason => "Bare newline in category" );
            return 1;
        }
    }

    my @locs = @{ $args{metadata}{locale} };
    foreach my $loc ( @locs ) {
        if ( $loc =~ m'http://'i ) {
            $class->notify_admins( %args, reason => "URL in locales field" );
            return 1;
        }
        if ( $loc =~ m'\n'i ) {
            $class->notify_admins( %args,
                                   reason => "Bare newline in locale" );
            return 1;
        }
    }

    # Everything below here only matches if we come via "Add a comment".
    if ( $args{via_add_comment} ) {

        if ( $args{added_comment} =~ m/mozhno\s+schitat\s+na\s+polovinu/ ) {
            $class->notify_admins( %args, reason => "mozhno schitat na polovinu" );
            return 1;
        }

        if ( $name eq "Chuen Cheng Ku, W1D 6PN" && $username =~ /@/ ) {
            $class->notify_admins( %args, reason => "CCK and \@ in username" );
            return 1;
        }

        if ( $args{added_comment} =~ m/rpz3zmr75a.com/is ) {
            $class->notify_admins( %args, reason => "rpz3zmr75a.com" );
            return 1;
        }
        if ( $args{added_comment} =~ m/myoff.forumup.co.za/is ) {
            $class->notify_admins( %args, reason => "myoff.forumup.co.za" );
            return 1;
        }
        if ( $args{added_comment} =~ m/peace.com/is ) {
            $class->notify_admins( %args, reason => "peace.com" );
            return 1;
        }
        if ( $args{added_comment} =~ m/look\s+for\s+some\s+my\s+links/is ) {
            $class->notify_admins( %args, reason => "look for some my links" );
            return 1;
        }
        if ( ( $args{added_comment} =~ /http:\/\/.*http:\/\//s )
             || ( $args{added_comment} =~ /a\s+href=.*a\s+href=/s ) ) {
            $class->notify_admins( %args, reason => "comment with more than one URL in" );
            return 1;
        }
        if ( $args{added_comment} =~ m{<a href=\s*></a>}is ) {
            $class->notify_admins( %args, reason => "malformed hyperlink in comment" );
            return 1;
        }
        if ( ( $content =~ /good\s+site\.\s+thank/i )
             || ( $content =~ /cool\s+site\.\s+thank/i )
             || ( $content =~ /nice\s+site\.\s+thank/i ) ) {
            if ( $content =~ 'http://' ) {
                $class->notify_admins( %args, reason => "'nice site' + URL" );
                return 1;
            }
        }

        if ( $username =~ /^[a-z]+\s[a-z]+$/ ) {
            my $text = "$username $args{added_comment}";
            if ( $text =~ /q[a-tv-z].*q[a-tv-z]/ ) {
                $class->notify_admins( %args, reason => "two-word lowercase username + two occurrences of q+non-u" );
                return 1;
            }
        }

        if ( $content =~ 'http://' && $content =~ /\banal\b/ && $content =~ /\bsex\b/ ) {
            $class->notify_admins( %args, reason => "'anal' + 'sex' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /\bxanax\b/ ) {
            $class->notify_admins( %args, reason => "'xanax' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /\bphentermine\b/ ) {
            $class->notify_admins( %args, reason => "'phentermine' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /\boxycodone\b/ ) {
            $class->notify_admins( %args, reason => "'oxycodone' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /free\s+video\s+download/ ) {
            $class->notify_admins( %args, reason => "'free video download' + URL" );
            return 1;
        }
    }
}

sub notify_admins {
    my ( $class, %args ) = @_;
    my $datestamp = localtime( time() );
    my $message = <<EOM;
From: kake\@earth.li
To: kake\@earth.li, bob\@randomness.org.uk
Date: $datestamp
Subject: Attempted spam edit on RGL

Someone just tried to edit RGL, and I said no because it looked like spam.
Here follows a dump of the details:

Reason: $args{reason}

EOM
    $message .= Dumper( \%args );

    my $sender = Email::Send->new( { mailer => "SMTP" } );
    $sender->mailer_args( [ Host => "localhost" ] );
    $sender->send( $message );
}

1;
